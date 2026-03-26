"""Tests for knowledge install command — skill link creation.

Covers the modified scenario from docs/features/knowledge.feature:
  'Install all knowledge packages from cliplin.yaml'
  — for each installed or updated package, if host integration supports skills,
    the CLI should create or refresh skill links under the host's skills directory.
"""
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
import yaml

from cliplin.commands.knowledge import knowledge_install_command


def _make_project(tmp_path: Path, ai_tool: str, packages: list) -> Path:
    """Set up a minimal project with cliplin.yaml."""
    config = {"ai_tool": ai_tool, "knowledge": packages}
    config_path = tmp_path / "cliplin.yaml"
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(config, f)
    return tmp_path


def _make_package_with_skills(pkg_path: Path, skill_names: list[str]) -> None:
    """Create a fake installed package with skill folders under skills/."""
    for skill_name in skill_names:
        skill_dir = pkg_path / "skills" / skill_name
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(f"# {skill_name}", encoding="utf-8")


class TestKnowledgeInstallCreatesSkillLinks:
    """knowledge install creates skill links for installed packages — same as knowledge add."""

    def test_install_creates_claude_skill_links_for_already_installed_package(self, tmp_path):
        """When package is already installed, knowledge install creates .claude/skills links."""
        packages = [{"name": "mypkg", "source": "github:org/repo", "version": "main"}]
        _make_project(tmp_path, "claude-code", packages)

        pkg_path = tmp_path / ".cliplin" / "knowledge" / "mypkg-github-org-repo"
        _make_package_with_skills(pkg_path, ["my-skill"])

        mock_store = MagicMock()
        mock_store.is_initialized.return_value = False

        with patch("cliplin.commands.knowledge.Path.cwd", return_value=tmp_path), \
             patch("cliplin.commands.knowledge.update_package_checkout"), \
             patch("cliplin.commands.knowledge.get_context_store", return_value=mock_store), \
             patch("cliplin.commands.knowledge.get_fingerprint_store", return_value=MagicMock()):
            knowledge_install_command(force=False)

        skill_link = tmp_path / ".claude" / "skills" / "my-skill" / "SKILL.md"
        assert skill_link.exists(), ".claude/skills/my-skill/SKILL.md was not created by knowledge install"

    def test_install_creates_cursor_skill_links_for_already_installed_package(self, tmp_path):
        """When package is already installed, knowledge install creates .cursor/skills links."""
        packages = [{"name": "mypkg", "source": "github:org/repo", "version": "main"}]
        _make_project(tmp_path, "cursor", packages)

        pkg_path = tmp_path / ".cliplin" / "knowledge" / "mypkg-github-org-repo"
        _make_package_with_skills(pkg_path, ["my-skill"])

        mock_store = MagicMock()
        mock_store.is_initialized.return_value = False

        with patch("cliplin.commands.knowledge.Path.cwd", return_value=tmp_path), \
             patch("cliplin.commands.knowledge.update_package_checkout"), \
             patch("cliplin.commands.knowledge.get_context_store", return_value=mock_store), \
             patch("cliplin.commands.knowledge.get_fingerprint_store", return_value=MagicMock()):
            knowledge_install_command(force=False)

        skill_link = tmp_path / ".cursor" / "skills" / "my-skill" / "SKILL.md"
        assert skill_link.exists(), ".cursor/skills/my-skill/SKILL.md was not created by knowledge install"

    def test_install_creates_gemini_skill_links_for_already_installed_package(self, tmp_path):
        """When package is already installed, knowledge install creates .gemini/skills links."""
        packages = [{"name": "mypkg", "source": "github:org/repo", "version": "main"}]
        _make_project(tmp_path, "gemini", packages)

        pkg_path = tmp_path / ".cliplin" / "knowledge" / "mypkg-github-org-repo"
        _make_package_with_skills(pkg_path, ["my-skill"])

        mock_store = MagicMock()
        mock_store.is_initialized.return_value = False

        with patch("cliplin.commands.knowledge.Path.cwd", return_value=tmp_path), \
             patch("cliplin.commands.knowledge.update_package_checkout"), \
             patch("cliplin.commands.knowledge.get_context_store", return_value=mock_store), \
             patch("cliplin.commands.knowledge.get_fingerprint_store", return_value=MagicMock()):
            knowledge_install_command(force=False)

        skill_link = tmp_path / ".gemini" / "skills" / "my-skill" / "SKILL.md"
        assert skill_link.exists(), ".gemini/skills/my-skill/SKILL.md was not created by knowledge install"

    def test_install_creates_skill_links_for_newly_installed_package(self, tmp_path):
        """When package is not yet installed, knowledge install clones it and creates skill links."""
        packages = [{"name": "mypkg", "source": "github:org/repo", "version": "main"}]
        _make_project(tmp_path, "claude-code", packages)

        pkg_path = tmp_path / ".cliplin" / "knowledge" / "mypkg-github-org-repo"

        def fake_clone(project_root, name, source, version):
            _make_package_with_skills(pkg_path, ["new-skill"])

        mock_store = MagicMock()
        mock_store.is_initialized.return_value = False

        with patch("cliplin.commands.knowledge.Path.cwd", return_value=tmp_path), \
             patch("cliplin.commands.knowledge.clone_package", side_effect=fake_clone), \
             patch("cliplin.commands.knowledge.get_context_store", return_value=mock_store), \
             patch("cliplin.commands.knowledge.get_fingerprint_store", return_value=MagicMock()):
            knowledge_install_command(force=False)

        skill_link = tmp_path / ".claude" / "skills" / "new-skill" / "SKILL.md"
        assert skill_link.exists(), ".claude/skills/new-skill/SKILL.md was not created after clone"

    def test_install_refreshes_existing_skill_links(self, tmp_path):
        """knowledge install refreshes (removes and recreates) pre-existing skill links."""
        packages = [{"name": "mypkg", "source": "github:org/repo", "version": "main"}]
        _make_project(tmp_path, "claude-code", packages)

        pkg_path = tmp_path / ".cliplin" / "knowledge" / "mypkg-github-org-repo"
        _make_package_with_skills(pkg_path, ["my-skill"])

        # Pre-create a stale link
        stale_dir = tmp_path / ".claude" / "skills" / "my-skill"
        stale_dir.mkdir(parents=True, exist_ok=True)
        (stale_dir / "SKILL.md").write_text("stale content", encoding="utf-8")

        mock_store = MagicMock()
        mock_store.is_initialized.return_value = False

        with patch("cliplin.commands.knowledge.Path.cwd", return_value=tmp_path), \
             patch("cliplin.commands.knowledge.update_package_checkout"), \
             patch("cliplin.commands.knowledge.get_context_store", return_value=mock_store), \
             patch("cliplin.commands.knowledge.get_fingerprint_store", return_value=MagicMock()):
            knowledge_install_command(force=False)

        skill_link = tmp_path / ".claude" / "skills" / "my-skill" / "SKILL.md"
        assert skill_link.exists()
        # Content should come from the package, not the stale file
        content = skill_link.read_text(encoding="utf-8")
        assert content == "# my-skill", f"Expected refreshed content, got: {content!r}"

    def test_install_skips_skill_linking_when_no_ai_tool_configured(self, tmp_path):
        """When cliplin.yaml has no ai_tool, knowledge install installs but creates no skill links."""
        packages = [{"name": "mypkg", "source": "github:org/repo", "version": "main"}]
        config = {"knowledge": packages}  # no ai_tool
        (tmp_path / "cliplin.yaml").write_text(yaml.safe_dump(config), encoding="utf-8")

        pkg_path = tmp_path / ".cliplin" / "knowledge" / "mypkg-github-org-repo"
        _make_package_with_skills(pkg_path, ["my-skill"])

        mock_store = MagicMock()
        mock_store.is_initialized.return_value = False

        with patch("cliplin.commands.knowledge.Path.cwd", return_value=tmp_path), \
             patch("cliplin.commands.knowledge.update_package_checkout"), \
             patch("cliplin.commands.knowledge.get_context_store", return_value=mock_store), \
             patch("cliplin.commands.knowledge.get_fingerprint_store", return_value=MagicMock()):
            knowledge_install_command(force=False)

        # No skill directories should have been created
        for host_dir in [".claude", ".cursor", ".gemini"]:
            skills_dir = tmp_path / host_dir / "skills"
            assert not skills_dir.exists(), f"{skills_dir} should not exist when no ai_tool is configured"

    def test_install_multiple_packages_creates_skill_links_for_all(self, tmp_path):
        """knowledge install creates skill links for every package that has skills."""
        packages = [
            {"name": "pkg1", "source": "github:org/repo1", "version": "main"},
            {"name": "pkg2", "source": "github:org/repo2", "version": "main"},
        ]
        _make_project(tmp_path, "claude-code", packages)

        for pkg_info in [("pkg1", "github:org/repo1", "skill-a"), ("pkg2", "github:org/repo2", "skill-b")]:
            name, source, skill = pkg_info
            normalized = f"{name}-{source.replace('github:', 'github-').replace('/', '-')}"
            pkg_path = tmp_path / ".cliplin" / "knowledge" / normalized
            _make_package_with_skills(pkg_path, [skill])

        mock_store = MagicMock()
        mock_store.is_initialized.return_value = False

        with patch("cliplin.commands.knowledge.Path.cwd", return_value=tmp_path), \
             patch("cliplin.commands.knowledge.update_package_checkout"), \
             patch("cliplin.commands.knowledge.get_context_store", return_value=mock_store), \
             patch("cliplin.commands.knowledge.get_fingerprint_store", return_value=MagicMock()):
            knowledge_install_command(force=False)

        assert (tmp_path / ".claude" / "skills" / "skill-a" / "SKILL.md").exists()
        assert (tmp_path / ".claude" / "skills" / "skill-b" / "SKILL.md").exists()
