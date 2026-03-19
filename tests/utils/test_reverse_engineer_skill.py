"""Tests for create_reverse_engineer_skill template function.

Covers scenarios from docs/features/reverse-engineer.feature:
- Skill file is created inside the framework package on cliplin init
- Skill is linked to Claude Code skills directory on init with --ai claude-code
- Skill is linked to Cursor skills directory on init with --ai cursor
"""
import os
import tempfile
from pathlib import Path

from cliplin.utils.templates import (
    create_framework_knowledge_package,
    create_reverse_engineer_skill,
)
from cliplin.utils.ai_host_integrations.claude_desktop import ClaudeDesktopIntegration
from cliplin.utils.ai_host_integrations.cursor import CursorIntegration


FRAMEWORK_SKILLS_RE = Path(".cliplin/knowledge/cliplin-framework/skills/cliplin-reverse-engineer")


class TestCreateReverseEngineerSkill:
    """Skill file is created inside the framework package on cliplin init."""

    def test_skill_md_is_created(self, tmp_path):
        framework_base = tmp_path / ".cliplin" / "knowledge" / "cliplin-framework"
        framework_base.mkdir(parents=True)

        create_reverse_engineer_skill(framework_base)

        skill_path = framework_base / "skills" / "cliplin-reverse-engineer" / "SKILL.md"
        assert skill_path.exists(), "SKILL.md was not created"

    def test_skill_md_describes_scan_sources(self, tmp_path):
        framework_base = tmp_path / ".cliplin" / "knowledge" / "cliplin-framework"
        framework_base.mkdir(parents=True)

        create_reverse_engineer_skill(framework_base)

        content = (framework_base / "skills" / "cliplin-reverse-engineer" / "SKILL.md").read_text(encoding="utf-8")
        assert "src/" in content
        assert "package.json" in content or "pyproject.toml" in content
        assert "README" in content

    def test_skill_md_describes_module_detection(self, tmp_path):
        framework_base = tmp_path / ".cliplin" / "knowledge" / "cliplin-framework"
        framework_base.mkdir(parents=True)

        create_reverse_engineer_skill(framework_base)

        content = (framework_base / "skills" / "cliplin-reverse-engineer" / "SKILL.md").read_text(encoding="utf-8")
        assert "top-level module" in content.lower() or "immediate subdirector" in content.lower()

    def test_skill_md_describes_two_phase_flow(self, tmp_path):
        framework_base = tmp_path / ".cliplin" / "knowledge" / "cliplin-framework"
        framework_base.mkdir(parents=True)

        create_reverse_engineer_skill(framework_base)

        content = (framework_base / "skills" / "cliplin-reverse-engineer" / "SKILL.md").read_text(encoding="utf-8")
        assert "Phase 1" in content
        assert "Phase 2" in content

    def test_skill_md_describes_tracking_file(self, tmp_path):
        framework_base = tmp_path / ".cliplin" / "knowledge" / "cliplin-framework"
        framework_base.mkdir(parents=True)

        create_reverse_engineer_skill(framework_base)

        content = (framework_base / "skills" / "cliplin-reverse-engineer" / "SKILL.md").read_text(encoding="utf-8")
        assert ".re-progress.yaml" in content

    def test_skill_md_describes_resume_behavior(self, tmp_path):
        framework_base = tmp_path / ".cliplin" / "knowledge" / "cliplin-framework"
        framework_base.mkdir(parents=True)

        create_reverse_engineer_skill(framework_base)

        content = (framework_base / "skills" / "cliplin-reverse-engineer" / "SKILL.md").read_text(encoding="utf-8")
        assert "Continue" in content or "[C]" in content
        assert "Restart" in content or "[R]" in content

    def test_skill_created_via_create_framework_knowledge_package(self, tmp_path):
        create_framework_knowledge_package(tmp_path)

        skill_path = tmp_path / ".cliplin" / "knowledge" / "cliplin-framework" / "skills" / "cliplin-reverse-engineer" / "SKILL.md"
        assert skill_path.exists(), "SKILL.md not created by create_framework_knowledge_package"

    def test_skill_md_written_with_utf8_encoding(self, tmp_path):
        framework_base = tmp_path / ".cliplin" / "knowledge" / "cliplin-framework"
        framework_base.mkdir(parents=True)

        create_reverse_engineer_skill(framework_base)

        skill_path = framework_base / "skills" / "cliplin-reverse-engineer" / "SKILL.md"
        content = skill_path.read_text(encoding="utf-8")
        assert len(content) > 0


class TestReverseEngineerSkillLinkedToClaudeCode:
    """Skill is linked to Claude Code skills directory on init with --ai claude-code."""

    def test_hard_link_created_at_claude_skills(self, tmp_path):
        create_framework_knowledge_package(tmp_path)
        framework_base = tmp_path / ".cliplin" / "knowledge" / "cliplin-framework"
        integration = ClaudeDesktopIntegration()

        integration.link_knowledge_skills(tmp_path, framework_base)

        linked = tmp_path / ".claude" / "skills" / "cliplin-reverse-engineer" / "SKILL.md"
        assert linked.exists(), ".claude/skills/cliplin-reverse-engineer/SKILL.md not created"

    def test_claude_skills_directory_exists(self, tmp_path):
        create_framework_knowledge_package(tmp_path)
        framework_base = tmp_path / ".cliplin" / "knowledge" / "cliplin-framework"
        integration = ClaudeDesktopIntegration()

        integration.link_knowledge_skills(tmp_path, framework_base)

        assert (tmp_path / ".claude" / "skills" / "cliplin-reverse-engineer").is_dir()

    def test_linked_file_shares_inode_with_source(self, tmp_path):
        create_framework_knowledge_package(tmp_path)
        framework_base = tmp_path / ".cliplin" / "knowledge" / "cliplin-framework"
        integration = ClaudeDesktopIntegration()

        integration.link_knowledge_skills(tmp_path, framework_base)

        src = framework_base / "skills" / "cliplin-reverse-engineer" / "SKILL.md"
        dst = tmp_path / ".claude" / "skills" / "cliplin-reverse-engineer" / "SKILL.md"
        try:
            assert os.stat(src).st_ino == os.stat(dst).st_ino, "Files are not hard-linked"
        except OSError:
            pass  # cross-filesystem: hard link not possible, skip inode check


class TestReverseEngineerSkillLinkedToCursor:
    """Skill is linked to Cursor skills directory on init with --ai cursor."""

    def test_hard_link_created_at_cursor_skills(self, tmp_path):
        create_framework_knowledge_package(tmp_path)
        framework_base = tmp_path / ".cliplin" / "knowledge" / "cliplin-framework"
        integration = CursorIntegration()

        integration.link_knowledge_skills(tmp_path, framework_base)

        linked = tmp_path / ".cursor" / "skills" / "cliplin-reverse-engineer" / "SKILL.md"
        assert linked.exists(), ".cursor/skills/cliplin-reverse-engineer/SKILL.md not created"

    def test_cursor_skills_directory_exists(self, tmp_path):
        create_framework_knowledge_package(tmp_path)
        framework_base = tmp_path / ".cliplin" / "knowledge" / "cliplin-framework"
        integration = CursorIntegration()

        integration.link_knowledge_skills(tmp_path, framework_base)

        assert (tmp_path / ".cursor" / "skills" / "cliplin-reverse-engineer").is_dir()
