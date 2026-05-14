"""Wibey AI integration: .wibey/mcp.json, .wibey/rules/*.md, and AGENTS.md at project root."""

import os
import shutil
import sys
from pathlib import Path

from rich.console import Console

from cliplin.utils import templates
from cliplin.utils.templates import FRAMEWORK_PACKAGE_DIR

console = Console()


class WibeyIntegration:
    """Integration handler for Wibey: .wibey/mcp.json, .wibey/rules/*.md, and AGENTS.md."""

    id = "wibey"
    rules_dir = ".wibey/rules"
    mcp_config_path = ".wibey/mcp.json"

    def apply(self, target_dir: Path) -> None:
        target_dir = Path(target_dir)
        rules_dir = target_dir / self.rules_dir
        rules_dir.mkdir(parents=True, exist_ok=True)

        templates.create_wibey_mcp_config(target_dir)

        rule_files = [
            ("feature-processing.md", templates.get_cursor_feature_processing_content),
            ("context-protocol-loading.md", templates.get_cursor_context_protocol_loading_content),
            ("feature-first-flow.md", templates.get_feature_first_flow_content),
            ("context.md", templates.get_cursor_context_content),
        ]
        for filename, getter in rule_files:
            file_path = f".wibey/rules/{filename}"
            (target_dir / file_path).write_text(getter(), encoding="utf-8")
            console.print(f"  [green]✓[/green] Created {file_path}")

        templates.merge_wibey_agents_md(target_dir)

        framework_base = target_dir / ".cliplin" / "knowledge" / FRAMEWORK_PACKAGE_DIR
        self.link_knowledge_skills(target_dir, framework_base)

    def link_knowledge_skills(self, project_root: Path, package_path: Path) -> None:
        """Create hard links from skill folders under package_path/skills/ to .wibey/skills/."""
        skills_src = package_path / "skills"
        if not skills_src.is_dir():
            return
        skills_dst_root = project_root / ".wibey" / "skills"
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
        """Remove from .wibey/skills/ the skill folders linked from this package."""
        skills_src = package_path / "skills"
        if not skills_src.is_dir():
            return
        skills_dst_root = project_root / ".wibey" / "skills"
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
