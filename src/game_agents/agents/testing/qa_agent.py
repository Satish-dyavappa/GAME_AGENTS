"""QA Agent: Executes automated tests, browser visual verification, and gameplay checks."""

from game_agents.agents.base.agent_config import AgentConfig
from game_agents.agents.base.base_agent import BaseAgent

QA_AGENT_SYSTEM_PROMPT = """You are the Game QA & Quality Assurance Agent.
Your duty is to verify that the game builds, runs without runtime errors, passes test suites, and renders correctly.

Testing Capabilities:
1. Run automated unit tests (`run_unit_tests`) and integration tests (`run_integration_tests`).
2. Launch browser previews and check for JavaScript runtime exceptions (`browser_console_logs`).
3. Capture visual gameplay snapshots to verify canvas rendering (`browser_screenshot`).
4. Simulate player button clicks and UI interaction (`browser_click`).
5. Execute shell test commands (`execute_command`).

Report your findings with clear PASS / FAIL verdicts, reproduction steps, and error logs.
"""


class QAAgent(BaseAgent):
    """QA Agent conducting automated and visual testing."""

    def __init__(self, **kwargs) -> None:
        config = AgentConfig(
            name="qa_agent",
            role="Game QA & Quality Assurance Engineer",
            system_prompt=QA_AGENT_SYSTEM_PROMPT,
            tools=[
                "run_unit_tests",
                "run_integration_tests",
                "browser_screenshot",
                "browser_click",
                "browser_console_logs",
                "read_file",
                "execute_command",
            ],
            temperature=0.1,
        )
        super().__init__(config=config, **kwargs)
