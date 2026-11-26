"""Base Agent implementation with tool execution loop and standardized results."""

import json
from abc import ABC
from datetime import datetime, timezone
from typing import Any, Callable
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from game_agents.agents.base.agent_config import AgentConfig
from game_agents.core.contracts.agent_result import AgentResult
from game_agents.core.contracts.project_manifest import ProjectManifest
from game_agents.core.contracts.task import Task
from game_agents.core.routing.model_router import (
    ApiKeyLoader,
    ModelRouter,
    ModelSelection,
    default_model_router,
)
from game_agents.tools.registry import ToolRegistry, default_tool_registry


class BaseAgent(ABC):
    """Foundational agent capable of tool-calling, autonomous multi-turn loops, and task execution."""

    def __init__(
        self,
        config: AgentConfig,
        tool_registry: ToolRegistry | None = None,
        model_router: ModelRouter | None = None,
        on_event: Callable[[str, dict[str, Any]], None] | None = None,
    ) -> None:
        self.config = config
        self.tool_registry = tool_registry or default_tool_registry
        self.model_router = model_router or default_model_router
        self.on_event = on_event

    def _emit(self, event_type: str, payload: dict[str, Any]) -> None:
        if self.on_event:
            try:
                self.on_event(event_type, payload)
            except Exception:
                pass

    def _get_allowed_tools(self) -> list[Any]:
        """Collect LangChain-compatible tools permitted for this agent."""
        allowed: list[Any] = []
        for name in self.config.tools:
            tool = self.tool_registry.get(name)
            if tool:
                lc_tool = tool.to_langchain_tool()
                if lc_tool is not None:
                    allowed.append(lc_tool)
        return allowed

    def _build_context_prompt(self, task: Task, manifest: ProjectManifest | None = None) -> str:
        """Compose human prompt incorporating task details and target engine manifest."""
        parts = [
            f"### Task: {task.title}",
            f"Description: {task.description}",
            f"Priority: {task.priority.value}",
        ]
        if task.engine:
            parts.append(f"Target Engine: {task.engine}")
        if manifest:
            parts.append(f"Project Engine: {manifest.engine.value}")
            parts.append(f"Project Root: {manifest.root_path}")
            if manifest.entry_point:
                parts.append(f"Entry Point: {manifest.entry_point}")
        if task.context:
            parts.append(f"Context: {json.dumps(task.context, indent=2)}")

        return "\n".join(parts)

    def run(self, task: Task, manifest: ProjectManifest | None = None) -> AgentResult:
        """Execute the task via an autonomous tool-calling loop."""
        task.start()
        files_created: set[str] = set()
        files_modified: set[str] = set()
        artifacts: dict[str, Any] = {}

        # 1. Resolve candidate models with automatic fallback on API key failures
        candidates = []
        try:
            primary_sel = self.model_router.select_model_for_task(task)
            candidates.append(primary_sel)
        except Exception:
            pass

        # Add active working providers as fallbacks (kilo, nvidia, openrouter)
        for prov in ["kilo", "nvidia", "openrouter"]:
            if not any(c.provider == prov for c in candidates):
                creds = ApiKeyLoader.get_all_credentials().get(prov)
                if creds and creds["available"]:
                    key = getattr(ApiKeyLoader, f"get_{prov}_key")()
                    candidates.append(
                        ModelSelection(
                            provider=prov,
                            model=creds["default_model"],
                            base_url=creds["base_url"],
                            api_key=key or "",
                            reason=f"Fallback provider {prov}",
                        )
                    )

        tools = self._get_allowed_tools()
        messages_init = [
            SystemMessage(content=self.config.system_prompt),
            HumanMessage(content=self._build_context_prompt(task, manifest)),
        ]

        last_error = None
        for sel in candidates:
            try:
                self._emit("agent_start", {"task": task.title, "provider": sel.provider, "model": sel.model})
                llm = self.model_router.get_chat_model(selection=sel)
                llm_with_tools = llm.bind_tools(tools) if tools else llm
                messages = list(messages_init)

                iterations = 0
                final_output = ""

                while iterations < self.config.max_iterations:
                    iterations += 1
                    ai_msg: AIMessage = llm_with_tools.invoke(messages)
                    messages.append(ai_msg)

                    tool_calls = getattr(ai_msg, "tool_calls", [])
                    if not tool_calls:
                        final_output = ai_msg.content if isinstance(ai_msg.content, str) else str(ai_msg.content)
                        break

                    for tc in tool_calls:
                        tool_name = tc.get("name", "")
                        tool_args = tc.get("args", {})
                        call_id = tc.get("id", f"call_{iterations}")

                        self._emit("tool_call", {"tool": tool_name, "args": tool_args})
                        tool_instance = self.tool_registry.get(tool_name)
                        if tool_instance:
                            tool_res = tool_instance(**tool_args)
                            content = tool_res.output if tool_res.success else f"ERROR: {tool_res.error}"
                            self._emit(
                                "tool_result",
                                {"tool": tool_name, "success": tool_res.success, "output": content[:240]},
                            )
                            if tool_name == "write_file" and "path" in tool_args:
                                files_created.add(str(tool_args["path"]))
                            elif tool_name == "edit_file" and "path" in tool_args:
                                files_modified.add(str(tool_args["path"]))
                        else:
                            content = f"Error: Tool '{tool_name}' is not recognized or not available."
                            self._emit("tool_result", {"tool": tool_name, "success": False, "output": content})

                        messages.append(ToolMessage(content=str(content), tool_call_id=call_id))

                if not final_output:
                    # Force one final summary response without tools so findings aren't lost
                    messages.append(
                        HumanMessage(
                            content="You have reached the tool call limit. Summarize your findings and final answer now without calling any more tools."
                        )
                    )
                    summary_msg = llm.invoke(messages)
                    final_output = (
                        summary_msg.content
                        if isinstance(summary_msg.content, str)
                        else str(summary_msg.content)
                    )

                self._emit(
                    "agent_finish",
                    {"success": True, "files_created": list(files_created), "files_modified": list(files_modified)},
                )

                result = AgentResult(
                    task_id=task.id,
                    agent_name=self.config.name,
                    success=True,
                    output=final_output,
                    files_created=list(files_created),
                    files_modified=list(files_modified),
                    artifacts=artifacts,
                    created_at=datetime.now(timezone.utc),
                )
                task.complete(result=result.model_dump())
                return result

            except Exception as e:
                last_error = e
                continue

        err_msg = f"Agent '{self.config.name}' failed: {str(last_error)}"
        task.fail(error=err_msg)
        return AgentResult(
            task_id=task.id,
            agent_name=self.config.name,
            success=False,
            output="",
            error=err_msg,
            created_at=datetime.now(timezone.utc),
        )
