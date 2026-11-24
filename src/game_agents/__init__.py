"""Game Dev Agents library."""

from game_agents.agents import (
    CodeReviewerAgent,
    DebuggerAgent,
    DeveloperAgent,
    PlannerAgent,
    ProjectAnalyzerAgent,
    QAAgent,
    SupervisorAgent,
)
from game_agents.core import (
    AgentResult,
    ApiKeyLoader,
    EngineType,
    ModelRouter,
    ProjectManifest,
    Status,
    Task,
    TaskPriority,
    TaskStatus,
    ToolResult,
    default_model_router,
)
from game_agents.engines import (
    BaseEngineAdapter,
    EngineRegistry,
    PhaserAdapter,
    ThreejsAdapter,
    UnityAdapter,
    UnrealAdapter,
    default_engine_registry,
)
from game_agents.tools import ToolRegistry, default_tool_registry
from game_agents.workflows import (
    BaseWorkflow,
    BugFixWorkflow,
    FeatureDevelopmentWorkflow,
    ProjectAnalysisWorkflow,
    WorkflowResult,
    WorkflowStatus,
    WorkflowStepResult,
)

__all__ = [
    # Contracts
    "Task",
    "Status",
    "TaskStatus",
    "TaskPriority",
    "AgentResult",
    "ToolResult",
    "EngineType",
    "ProjectManifest",
    # Model Routing
    "ApiKeyLoader",
    "ModelRouter",
    "default_model_router",
    # Tools
    "ToolRegistry",
    "default_tool_registry",
    # Engines
    "BaseEngineAdapter",
    "EngineRegistry",
    "default_engine_registry",
    "PhaserAdapter",
    "UnityAdapter",
    "UnrealAdapter",
    "ThreejsAdapter",
    # Agents
    "SupervisorAgent",
    "PlannerAgent",
    "ProjectAnalyzerAgent",
    "DeveloperAgent",
    "DebuggerAgent",
    "CodeReviewerAgent",
    "QAAgent",
    # Workflows
    "BaseWorkflow",
    "WorkflowResult",
    "WorkflowStatus",
    "WorkflowStepResult",
    "ProjectAnalysisWorkflow",
    "FeatureDevelopmentWorkflow",
    "BugFixWorkflow",
]
