"""OpenCode AI integration: opencode.json and OPENCODE.md at project root."""

import os
import shutil
import sys
from pathlib import Path

from rich.console import Console

from cliplin.utils import templates
from cliplin.utils.templates import FRAMEWORK_PACKAGE_DIR

console = Console()


class OpenCodeIntegration:
    """Integration handler for OpenCode AI: opencode.json and OPENCODE.md at project root."""

    id = "opencode"
    rules_dir = "."
    mcp_config_path = "opencode.json"

    def apply(self, target_dir: Path) -> None:
        target_dir = Path(target_dir)

        templates.create_opencode_config(target_dir)

        opencode_md_path = target_dir / "OPENCODE.md"
        opencode_md_path.write_text(
            templates.get_opencode_opencode_md_content(),
            encoding="utf-8",
        )
        console.print(f"  [green]✓[/green] Created/updated {opencode_md_path.name}")

        framework_base = target_dir / ".cliplin" / "knowledge" / FRAMEWORK_PACKAGE_DIR
        self.link_knowledge_skills(target_dir, framework_base)

    def link_knowledge_skills(self, project_root: Path, package_path: Path) -> None:
        """Create hard links from skill folders under package_path/skills/ to .opencode/skills/."""
        skills_src = package_path / "skills"
        if not skills_src.is_dir():
            return
        skills_dst_root = project_root / ".opencode" / "skills"
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
        """Remove from .opencode/skills/ the skill folders linked from this package."""
        skills_src = package_path / "skills"
        if not skills_src.is_dir():
            return
        skills_dst_root = project_root / ".opencode" / "skills"
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
