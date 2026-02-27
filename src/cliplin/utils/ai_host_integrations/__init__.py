"""AI host integrations: one class per host, registry, and create_ai_tool_config entry point."""

from pathlib import Path

from cliplin.utils.ai_host_integrations.base import (
    AiHostIntegration,
    get_integration,
    get_known_ai_tool_ids,
    register_integration,
)
from cliplin.utils.ai_host_integrations.claude_desktop import ClaudeDesktopIntegration
from cliplin.utils.ai_host_integrations.cursor import CursorIntegration
from cliplin.utils.ai_host_integrations.gemini_cli import GeminiCliIntegration

# Register built-in integrations so create_ai_tool_config and validate can resolve by id
register_integration(CursorIntegration())
register_integration(ClaudeDesktopIntegration())
register_integration(GeminiCliIntegration())


def create_ai_tool_config(target_dir: Path, ai_tool: str) -> None:
    """Create AI tool-specific configuration files by delegating to the host integration."""
    integration = get_integration(ai_tool)
    if integration is None:
        raise ValueError(
            f"Unknown AI tool: {ai_tool}. Available: {', '.join(get_known_ai_tool_ids())}"
        )
    integration.apply(target_dir)


__all__ = [
    "AiHostIntegration",
    "create_ai_tool_config",
    "get_integration",
    "get_known_ai_tool_ids",
]
