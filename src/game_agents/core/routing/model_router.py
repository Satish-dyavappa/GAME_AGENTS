"""API key management and intelligent task-based model router.

Loads API keys for all providers (Kilo, OpenRouter, OpenAI, Gemini, Groq, Ollama)
and dynamically selects the optimal model depending on the task requirements.
"""

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import yaml
from dotenv import find_dotenv, load_dotenv
from pydantic import BaseModel, Field

from game_agents.core.contracts.task import Task, TaskPriority

# Automatically load environment variables from .env
load_dotenv(find_dotenv(usecwd=True))


@dataclass
class ProviderInfo:
    """Configuration and credentials for a model provider."""

    name: str
    api_key: str | None
    base_url: str
    default_model: str
    is_available: bool
    free_models: list[str]


class ModelSelection(BaseModel):
    """The resolved model and routing decision for a given task."""

    provider: str = Field(..., description="Provider name (kilo, openrouter, openai, gemini, groq, ollama)")
    model: str = Field(..., description="Specific model identifier")
    base_url: str = Field(..., description="API base URL")
    api_key: str = Field(default="", description="API key to use")
    temperature: float = Field(default=0.2, description="Sampling temperature")
    max_tokens: int = Field(default=4096, description="Max output tokens")
    reason: str = Field(..., description="Explanation of why this model was selected for the task")


class ApiKeyLoader:
    """Loads and validates API credentials across all supported sites."""

    @staticmethod
    def get_kilo_key() -> str | None:
        return os.getenv("KILO_API_KEY")

    @staticmethod
    def get_openrouter_key() -> str | None:
        return os.getenv("OPENROUTER_API_KEY")

    @staticmethod
    def get_openai_key() -> str | None:
        return os.getenv("OPENAI_API_KEY") or os.getenv("GPT_API_KEY")

    @staticmethod
    def get_gemini_key() -> str | None:
        return os.getenv("GEMINI_API_KEY")

    @staticmethod
    def get_groq_key() -> str | None:
        return os.getenv("GROQ_API_KEY")

    @staticmethod
    def get_tavily_key() -> str | None:
        return os.getenv("TAVILY_API_KEY")

    @classmethod
    def get_all_credentials(cls) -> dict[str, dict[str, Any]]:
        """Return a summary of all known providers and whether their keys are present."""
        return {
            "kilo": {
                "available": bool(cls.get_kilo_key()),
                "base_url": os.getenv("KILO_BASE_URL", "https://api.kilo.ai/api/gateway/v1/"),
                "default_model": os.getenv("KILO_MODEL", "kilo-auto/free"),
            },
            "openrouter": {
                "available": bool(cls.get_openrouter_key()),
                "base_url": os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
                "default_model": os.getenv("OPENROUTER_MODEL", "qwen/qwen-2.5-coder-32b-instruct:free"),
            },
            "openai": {
                "available": bool(cls.get_openai_key()),
                "base_url": "https://api.openai.com/v1",
                "default_model": os.getenv("GPT_MODEL", "gpt-4o"),
            },
            "gemini": {
                "available": bool(cls.get_gemini_key()),
                "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
                "default_model": os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            },
            "groq": {
                "available": bool(cls.get_groq_key()),
                "base_url": "https://api.groq.com/openai/v1",
                "default_model": os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            },
            "ollama": {
                "available": True,  # Local provider, no remote API key required
                "base_url": "http://localhost:11434/v1",
                "default_model": "deepseek-coder:6.7b",
            },
        }


class ModelRouter:
    """Intelligently routes tasks to the optimal LLM provider and model.

    Evaluates task complexity, domain (coding vs planning vs quick edits),
    and priority to select the best AI model.
    """

    def __init__(self, config_path: str = "config/models.yaml") -> None:
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> dict[str, Any]:
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f) or {}
            except Exception:
                pass
        return {}

    def get_available_providers(self) -> list[str]:
        """List provider names that have active credentials configured."""
        creds = ApiKeyLoader.get_all_credentials()
        return [name for name, data in creds.items() if data["available"]]

    def select_model_for_task(self, task: Task) -> ModelSelection:
        """Analyze a Task and return the ideal provider and model configuration."""
        available = self.get_available_providers()
        if not available:
            # Fallback to local Ollama if no cloud keys configured
            return ModelSelection(
                provider="ollama",
                model="deepseek-coder:6.7b",
                base_url="http://localhost:11434/v1",
                reason="No remote API keys detected. Falling back to local Ollama.",
            )

        text = f"{task.title} {task.description}".lower()

        # 1. Complex Architecture / Multi-Agent Planning / Hard Bugfix (Needs deep reasoning)
        is_high_reasoning = (
            task.priority == TaskPriority.CRITICAL
            or any(kw in text for kw in ["architect", "system design", "refactor whole", "planning", "security audit"])
        )
        if is_high_reasoning:
            if "openai" in available and ApiKeyLoader.get_openai_key():
                return ModelSelection(
                    provider="openai",
                    model=os.getenv("GPT_MODEL", "gpt-4o"),
                    base_url="https://api.openai.com/v1",
                    api_key=ApiKeyLoader.get_openai_key() or "",
                    reason="Critical architecture/planning task routed to top-tier reasoning model (GPT-4o).",
                )
            if "openrouter" in available:
                return ModelSelection(
                    provider="openrouter",
                    model="deepseek/deepseek-r1:free",
                    base_url="https://openrouter.ai/api/v1",
                    api_key=ApiKeyLoader.get_openrouter_key() or "",
                    reason="High reasoning task routed to DeepSeek-R1 (Reasoning model via OpenRouter).",
                )

        # 2. Game Programming & Code Generation (Needs specialized code intelligence)
        is_coding = any(
            kw in text
            for kw in [
                "write", "code", "implement", "script", "function", "class", "phaser",
                "unity", "unreal", "godot", "shader", "controller", "movement", "physics"
            ]
        )
        if is_coding:
            # Prefer Qwen 2.5 Coder via OpenRouter or Kilo
            if "openrouter" in available:
                return ModelSelection(
                    provider="openrouter",
                    model="qwen/qwen-2.5-coder-32b-instruct:free",
                    base_url="https://openrouter.ai/api/v1",
                    api_key=ApiKeyLoader.get_openrouter_key() or "",
                    reason="Game programming task routed to Qwen-2.5-Coder (Top code-specialized model).",
                )
            if "kilo" in available:
                return ModelSelection(
                    provider="kilo",
                    model=os.getenv("KILO_MODEL", "kilo-auto/free"),
                    base_url=os.getenv("KILO_BASE_URL", "https://api.kilo.ai/api/gateway/v1/"),
                    api_key=ApiKeyLoader.get_kilo_key() or "",
                    reason="Game programming task routed to Kilo AI auto coding router.",
                )
            if "gemini" in available:
                return ModelSelection(
                    provider="gemini",
                    model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
                    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
                    api_key=ApiKeyLoader.get_gemini_key() or "",
                    reason="Fast game coding routed to Google Gemini Flash.",
                )

        # 3. Fast Iterations / Testing / Linting / Minor Edits
        is_quick = any(kw in text for kw in ["test", "lint", "format", "check", "inspect", "search", "list"])
        if is_quick:
            if "groq" in available and ApiKeyLoader.get_groq_key():
                return ModelSelection(
                    provider="groq",
                    model="llama-3.1-8b-instant",
                    base_url="https://api.groq.com/openai/v1",
                    api_key=ApiKeyLoader.get_groq_key() or "",
                    reason="Low latency test/inspection task routed to Groq ultra-fast tier.",
                )
            if "kilo" in available:
                return ModelSelection(
                    provider="kilo",
                    model="kilo-auto/free",
                    base_url=os.getenv("KILO_BASE_URL", "https://api.kilo.ai/api/gateway/v1/"),
                    api_key=ApiKeyLoader.get_kilo_key() or "",
                    reason="Quick iteration task routed to Kilo Free tier.",
                )

        # 4. Default: User's configured default provider from models.yaml or .env
        default_p = self.config.get("default_provider", os.getenv("ACTIVE_PROVIDER", "kilo"))
        if default_p in available:
            creds = ApiKeyLoader.get_all_credentials()[default_p]
            key = getattr(ApiKeyLoader, f"get_{default_p}_key")() if hasattr(ApiKeyLoader, f"get_{default_p}_key") else ""
            return ModelSelection(
                provider=default_p,
                model=creds["default_model"],
                base_url=creds["base_url"],
                api_key=key or "",
                reason=f"Task routed to default configured provider ({default_p}).",
            )

        # 5. Fallback to any first available provider
        first_p = available[0]
        first_creds = ApiKeyLoader.get_all_credentials()[first_p]
        key = getattr(ApiKeyLoader, f"get_{first_p}_key")() if hasattr(ApiKeyLoader, f"get_{first_p}_key") else ""
        return ModelSelection(
            provider=first_p,
            model=first_creds["default_model"],
            base_url=first_creds["base_url"],
            api_key=key or "",
            reason=f"Task routed to available provider fallback ({first_p}).",
        )

    def get_chat_model(self, selection: ModelSelection | None = None, task: Task | None = None) -> Any:
        """Instantiate a LangChain chat model ready for agent execution."""
        from langchain_openai import ChatOpenAI

        if selection is None:
            if task is None:
                raise ValueError("Must provide either a ModelSelection or a Task")
            selection = self.select_model_for_task(task)

        # Return OpenAI-compatible LangChain Chat model
        return ChatOpenAI(
            model=selection.model,
            api_key=selection.api_key or "no-key",
            base_url=selection.base_url,
            temperature=selection.temperature,
            max_tokens=selection.max_tokens,
        )


# Global singleton router instance
default_model_router = ModelRouter()
