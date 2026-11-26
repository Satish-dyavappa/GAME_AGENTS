"""Debugger Agent: Diagnoses compile errors, runtime crashes, and engine bugs."""

from game_agents.agents.base.agent_config import AgentConfig
from game_agents.agents.base.base_agent import BaseAgent

DEBUGGER_SYSTEM_PROMPT = """You are the Game Debugger Agent.
Your mission is to isolate, diagnose, and fix game bugs, compile failures, and runtime exceptions.

Debugging Workflow:
1. Collect error traces from browser console logs (`browser_console_logs`) or compiler output (`execute_command`).
2. Read the offending source file using `read_file`.
3. Understand the root cause (null pointer, undefined property, incorrect physics call, missing asset).
4. Apply precise minimal surgical fixes using `edit_file`.
5. Verify the fix by re-running tests or inspecting the logs.

Never make wild guesses; verify with logs and file reads.
"""


class DebuggerAgent(BaseAgent):
    """Debugger Agent resolving runtime and compile errors."""

    def __init__(self, **kwargs) -> None:
        config = AgentConfig(
            name="debugger",
            role="Game Bug Fix & Troubleshooting Specialist",
            system_prompt=DEBUGGER_SYSTEM_PROMPT,
            tools=[
                "read_file",
                "edit_file",
                "write_file",
                "browser_console_logs",
                "execute_command",
                "search_files",
                "inspect_components",
                "search_docs",
            ],
            temperature=0.1,
            max_iterations=40,
        )
        super().__init__(config=config, **kwargs)
