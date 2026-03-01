"""Claude Desktop integration: config and rules under .mcp.json and .claude/."""

import os
import shutil
from pathlib import Path

from rich.console import Console

from cliplin.utils import templates

console = Console()


class ClaudeDesktopIntegration:
    """Integration handler for Claude Code / Claude Desktop: .mcp.json and .claude/rules/ + instructions."""

    id = "claude-code"
    rules_dir = ".claude/rules"
    mcp_config_path = ".mcp.json"

    def apply(self, target_dir: Path) -> None:
        target_dir = Path(target_dir)
        rules_dir = target_dir / self.rules_dir
        rules_dir.mkdir(parents=True, exist_ok=True)

        templates.create_claude_desktop_mcp_config(target_dir)

        feature_file_path = ".claude/rules/feature-processing.md"
        (target_dir / feature_file_path).write_text(
            templates.get_cursor_feature_processing_content(), encoding="utf-8"
        )
        console.print(f"  [green]✓[/green] Created {feature_file_path}")

        protocol_file_path = ".claude/rules/context-protocol-loading.md"
        (target_dir / protocol_file_path).write_text(
            templates.get_cursor_context_protocol_loading_content(), encoding="utf-8"
        )
        console.print(f"  [green]✓[/green] Created {protocol_file_path}")

        flow_file_path = ".claude/rules/feature-first-flow.md"
        (target_dir / flow_file_path).write_text(
            templates.get_feature_first_flow_content(), encoding="utf-8"
        )
        console.print(f"  [green]✓[/green] Created {flow_file_path}")

        context_file_path = ".claude/rules/context.md"
        (target_dir / context_file_path).write_text(
            templates.get_cursor_context_content(), encoding="utf-8"
        )
        console.print(f"  [green]✓[/green] Created {context_file_path}")

        instructions_path = ".claude/instructions.md"
        (target_dir / instructions_path).write_text(
            templates.get_claude_desktop_instructions_content(), encoding="utf-8"
        )
        console.print(f"  [green]✓[/green] Created {instructions_path}")

        claude_md_path = ".claude/claude.md"
        (target_dir / claude_md_path).write_text(
            templates.get_claude_desktop_claude_md_content(), encoding="utf-8"
        )
        console.print(f"  [green]✓[/green] Created {claude_md_path}")

    def link_knowledge_skills(self, project_root: Path, package_path: Path) -> None:
        """Create hard links from skill folders (those containing SKILL.md) to .claude/skills/ so Claude sees them.
        Claude expects one level: .claude/skills/<skill_name>/SKILL.md.
        Finds all folders under package_path/skills/ that contain SKILL.md and links each
        directly to .claude/skills/<folder_name>, handling both layouts:
        - skills/skill-folder/SKILL.md -> .claude/skills/skill-folder/
        - skills/<pkg-repo>/skill-folder/SKILL.md -> .claude/skills/skill-folder/ (skips wrapper level)"""
        skills_src = package_path / "skills"
        if not skills_src.is_dir():
            return
        skills_dst_root = project_root / ".claude" / "skills"
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
                except OSError:
                    pass  # e.g. cross-filesystem: skip; hard links only

    def unlink_knowledge_skills(self, project_root: Path, package_path: Path) -> None:
        """Remove from .claude/skills/ the skill folders that were linked from this package.
        Finds all folders under package_path/skills/ that contain SKILL.md and removes each."""
        skills_src = package_path / "skills"
        if not skills_src.is_dir():
            return
        skills_dst_root = project_root / ".claude" / "skills"
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
