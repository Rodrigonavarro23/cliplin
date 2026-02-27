"""Gemini CLI integration: .gemini/settings.json and GEMINI.md at project root."""

from pathlib import Path

from rich.console import Console

from cliplin.utils import templates

console = Console()


class GeminiCliIntegration:
    """Integration handler for Gemini CLI: .gemini/settings.json and GEMINI.md."""

    id = "gemini"
    # For Gemini CLI, rules live in GEMINI.md at project root.
    rules_dir = "."
    # validate_command uses this path to check that Gemini settings exist.
    mcp_config_path = ".gemini/settings.json"

    def apply(self, target_dir: Path) -> None:
        target_dir = Path(target_dir)

        # Ensure Gemini CLI settings exist and include Cliplin MCP configuration.
        templates.create_gemini_cli_settings(target_dir)

        # Create or update GEMINI.md with consolidated project rules for Gemini CLI.
        gemini_md_path = target_dir / "GEMINI.md"
        gemini_md_path.write_text(
            templates.get_gemini_gemini_md_content(),
            encoding="utf-8",
        )
        console.print(f"  [green]✓[/green] Created/updated {gemini_md_path.name}")

