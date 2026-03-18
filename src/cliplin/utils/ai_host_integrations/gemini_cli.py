"""Gemini CLI integration: .gemini/settings.json and GEMINI.md at project root."""

import os
import shutil
import sys
from pathlib import Path

from rich.console import Console

from cliplin.utils import templates
from cliplin.utils.templates import FRAMEWORK_PACKAGE_DIR

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

        framework_base = target_dir / ".cliplin" / "knowledge" / FRAMEWORK_PACKAGE_DIR
        self.link_knowledge_skills(target_dir, framework_base)

    def link_knowledge_skills(self, project_root: Path, package_path: Path) -> None:
        """Create hard links from skill folders (those containing SKILL.md) to .gemini/skills/ so Gemini sees them.
        Gemini expects one level: .gemini/skills/<skill_name>/SKILL.md.
        Finds all folders under package_path/skills/ that contain SKILL.md and links each
        directly to .gemini/skills/<folder_name>, handling both layouts:
        - skills/skill-folder/SKILL.md -> .gemini/skills/skill-folder/
        - skills/<pkg-repo>/skill-folder/SKILL.md -> .gemini/skills/skill-folder/ (skips wrapper level)"""
        skills_src = package_path / "skills"
        if not skills_src.is_dir():
            return
        skills_dst_root = project_root / ".gemini" / "skills"
        skills_dst_root.mkdir(parents=True, exist_ok=True)
        skill_folders: list[Path] = []
        for path in skills_src.rglob("SKILL.md"):
            if path.is_file():
                skill_folders.append(path.parent)
        for skill_dir in skill_folders:
            dst_folder = skills_dst_root / skill_dir.name
            if dst_folder.exists():
                shutil.rmtree(dst_folder)
            dst_folder.mkdir(parents=True, exist_ok=True)
            for src_file in skill_dir.rglob("*"):
                if not src_file.is_file():
                    continue
                rel = src_file.relative_to(skill_dir)
                dst_file = dst_folder / rel
                dst_file.parent.mkdir(parents=True, exist_ok=True)
                if dst_file.exists():
                    dst_file.unlink()
                try:
                    os.link(src_file, dst_file)
                except OSError as exc:
                    print(
                        f"  warning: could not hard-link {src_file} -> {dst_file}: {exc}",
                        file=sys.stderr,
                    )

    def unlink_knowledge_skills(self, project_root: Path, package_path: Path) -> None:
        """Remove from .gemini/skills/ the skill folders that were linked from this package.
        Finds all folders under package_path/skills/ that contain SKILL.md and removes each."""
        skills_src = package_path / "skills"
        if not skills_src.is_dir():
            return
        skills_dst_root = project_root / ".gemini" / "skills"
        if not skills_dst_root.exists():
            return
        skill_folder_names: set[str] = set()
        for path in skills_src.rglob("SKILL.md"):
            if path.is_file():
                skill_folder_names.add(path.parent.name)
        for name in skill_folder_names:
            dst_folder = skills_dst_root / name
            if dst_folder.exists():
                shutil.rmtree(dst_folder)

