"""Base Agent implementation with tool execution loop and standardized results."""

import json
from abc import ABC
from datetime import datetime, timezone
from typing import Any
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from game_agents.agents.base.agent_config import AgentConfig
from game_agents.core.contracts.agent_result import AgentResult
from game_agents.core.contracts.project_manifest import ProjectManifest
from game_agents.core.contracts.task import Task
from game_agents.core.routing.model_router import ModelRouter, default_model_router
from game_agents.tools.registry import ToolRegistry, default_tool_registry


class BaseAgent(ABC):
    """Foundational agent capable of tool-calling, autonomous multi-turn loops, and task execution."""

    def __init__(
        self,
        config: AgentConfig,
        tool_registry: ToolRegistry | None = None,
        model_router: ModelRouter | None = None,
    ) -> None:
        self.config = config
        self.tool_registry = tool_registry or default_tool_registry
        self.model_router = model_router or default_model_router

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

        try:
            # 1. Resolve LLM model for this task
            llm = self.model_router.get_chat_model(task=task)

            # 2. Bind permitted tools to LLM
            tools = self._get_allowed_tools()
            llm_with_tools = llm.bind_tools(tools) if tools else llm

            # 3. Initialize message history
            messages = [
                SystemMessage(content=self.config.system_prompt),
                HumanMessage(content=self._build_context_prompt(task, manifest)),
            ]

            iterations = 0
            final_output = ""

            # 4. Multi-turn autonomous tool execution loop
            while iterations < self.config.max_iterations:
                iterations += 1
                ai_msg: AIMessage = llm_with_tools.invoke(messages)
                messages.append(ai_msg)

                # Check if the model called tools
                tool_calls = getattr(ai_msg, "tool_calls", [])
                if not tool_calls:
                    final_output = ai_msg.content if isinstance(ai_msg.content, str) else str(ai_msg.content)
                    break

                # Execute requested tools
                for tc in tool_calls:
                    tool_name = tc.get("name", "")
                    tool_args = tc.get("args", {})
                    call_id = tc.get("id", f"call_{iterations}")

                    tool_instance = self.tool_registry.get(tool_name)
                    if tool_instance:
                        tool_res = tool_instance(**tool_args)
                        content = tool_res.output if tool_res.success else f"ERROR: {tool_res.error}"

                        # Track modified/created files
                        if tool_name == "write_file" and "path" in tool_args:
                            files_created.add(str(tool_args["path"]))
                        elif tool_name == "edit_file" and "path" in tool_args:
                            files_modified.add(str(tool_args["path"]))
                    else:
                        content = f"Error: Tool '{tool_name}' is not recognized or not available."

                    messages.append(ToolMessage(content=str(content), tool_call_id=call_id))

            if not final_output:
                final_output = "Task iteration limit reached without explicit final response."

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
            err_msg = f"Agent '{self.config.name}' failed: {str(e)}"
            task.fail(error=err_msg)
            return AgentResult(
                task_id=task.id,
                agent_name=self.config.name,
                success=False,
                output="",
                error=err_msg,
                created_at=datetime.now(timezone.utc),
            )
