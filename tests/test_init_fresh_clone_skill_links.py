"""Tests for cliplin init — fresh-clone knowledge package skill linking.

Covers the modified scenario from docs/features/cli.feature:
  'Handle initialization in non-empty directory'
  — regardless of whether Cliplin was already initialized, if cliplin.yaml
    declares knowledge packages the CLI should run knowledge install at the
    end of init to install packages and create skill links.
"""
from pathlib import Path
from unittest.mock import patch, MagicMock, call

import pytest
import yaml

from cliplin.commands.init import init_command


def _write_cliplin_yaml(project_root: Path, ai_tool: str, packages: list) -> None:
    config = {"ai_tool": ai_tool, "knowledge": packages}
    (project_root / "cliplin.yaml").write_text(
        yaml.safe_dump(config), encoding="utf-8"
    )


def _make_package_with_skills(pkg_path: Path, skill_names: list[str]) -> None:
    for skill_name in skill_names:
        skill_dir = pkg_path / "skills" / skill_name
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(f"# {skill_name}", encoding="utf-8")


class TestInitFreshCloneSkillLinks:
    """On first cliplin init, knowledge packages declared in cliplin.yaml get installed and skill-linked."""

    def _base_mocks(self, tmp_path):
        """Return a dict of patches that stub out heavy init operations."""
        mock_client = MagicMock()
        mock_store = MagicMock()
        mock_store.is_initialized.return_value = False
        mock_fingerprint = MagicMock()
        return {
            "cliplin.commands.init.Path.cwd": lambda *a, **kw: tmp_path,
            "cliplin.commands.init.get_chromadb_client": lambda *a, **kw: mock_client,
            "cliplin.commands.init.get_context_store": lambda *a, **kw: mock_store,
            "cliplin.commands.init.initialize_collections": MagicMock(),
            "cliplin.commands.init.get_fingerprint_store": lambda *a, **kw: mock_fingerprint,
            "cliplin.commands.init.create_framework_knowledge_package": MagicMock(),
            "cliplin.commands.init._reindex_framework_package": MagicMock(),
            "cliplin.commands.init.validate_project_structure": MagicMock(),
            "cliplin.commands.knowledge.get_context_store": lambda *a, **kw: mock_store,
            "cliplin.commands.knowledge.get_fingerprint_store": lambda *a, **kw: mock_fingerprint,
        }

    def test_first_init_creates_skill_links_when_packages_declared(self, tmp_path):
        """First cliplin init on a fresh clone creates skill links for declared knowledge packages."""
        packages = [{"name": "mypkg", "source": "github:org/repo", "version": "main"}]
        _write_cliplin_yaml(tmp_path, "claude-code", packages)

        pkg_path = tmp_path / ".cliplin" / "knowledge" / "mypkg-github-org-repo"
        _make_package_with_skills(pkg_path, ["my-skill"])

        with patch("cliplin.commands.init.Path.cwd", return_value=tmp_path), \
             patch("cliplin.commands.init.get_chromadb_client", return_value=MagicMock()), \
             patch("cliplin.commands.init.initialize_collections"), \
             patch("cliplin.commands.init.create_framework_knowledge_package"), \
             patch("cliplin.commands.init._reindex_framework_package"), \
             patch("cliplin.commands.init.validate_project_structure"), \
             patch("cliplin.commands.init.create_ai_tool_config"), \
             patch("cliplin.commands.knowledge.update_package_checkout"), \
             patch("cliplin.commands.knowledge.Path.cwd", return_value=tmp_path), \
             patch("cliplin.commands.knowledge.get_context_store", return_value=MagicMock(is_initialized=lambda: False)), \
             patch("cliplin.commands.knowledge.get_fingerprint_store", return_value=MagicMock()):
            init_command(ai=None)

        skill_link = tmp_path / ".claude" / "skills" / "my-skill" / "SKILL.md"
        assert skill_link.exists(), (
            "On first init with pre-declared knowledge packages, "
            ".claude/skills/my-skill/SKILL.md was not created"
        )

    def test_first_init_no_skill_links_when_no_packages(self, tmp_path):
        """First cliplin init with no knowledge packages does not create any skill dirs."""
        (tmp_path / "cliplin.yaml").write_text(
            yaml.safe_dump({"ai_tool": "claude-code"}), encoding="utf-8"
        )

        with patch("cliplin.commands.init.Path.cwd", return_value=tmp_path), \
             patch("cliplin.commands.init.get_chromadb_client", return_value=MagicMock()), \
             patch("cliplin.commands.init.initialize_collections"), \
             patch("cliplin.commands.init.create_framework_knowledge_package"), \
             patch("cliplin.commands.init._reindex_framework_package"), \
             patch("cliplin.commands.init.validate_project_structure"), \
             patch("cliplin.commands.init.create_ai_tool_config"):
            init_command(ai=None)

        skills_dir = tmp_path / ".claude" / "skills"
        assert not skills_dir.exists() or not any(skills_dir.iterdir()), (
            "No skill dirs should be created when no knowledge packages are declared"
        )

    def test_reinit_still_creates_skill_links(self, tmp_path):
        """Re-running cliplin init on an already-initialized project still creates skill links."""
        packages = [{"name": "mypkg", "source": "github:org/repo", "version": "main"}]
        _write_cliplin_yaml(tmp_path, "claude-code", packages)

        # Simulate already initialized: create .cliplin/data/context
        (tmp_path / ".cliplin" / "data" / "context").mkdir(parents=True)

        pkg_path = tmp_path / ".cliplin" / "knowledge" / "mypkg-github-org-repo"
        _make_package_with_skills(pkg_path, ["my-skill"])

        with patch("cliplin.commands.init.Path.cwd", return_value=tmp_path), \
             patch("cliplin.commands.init.get_chromadb_client", return_value=MagicMock()), \
             patch("cliplin.commands.init.initialize_collections"), \
             patch("cliplin.commands.init.create_framework_knowledge_package"), \
             patch("cliplin.commands.init._reindex_framework_package"), \
             patch("cliplin.commands.init.validate_project_structure"), \
             patch("cliplin.commands.init.create_ai_tool_config"), \
             patch("cliplin.commands.knowledge.update_package_checkout"), \
             patch("cliplin.commands.knowledge.Path.cwd", return_value=tmp_path), \
             patch("cliplin.commands.knowledge.get_context_store", return_value=MagicMock(is_initialized=lambda: False)), \
             patch("cliplin.commands.knowledge.get_fingerprint_store", return_value=MagicMock()), \
             patch("builtins.input", return_value="y"), \
             patch("typer.confirm", return_value=True):
            init_command(ai=None)

        skill_link = tmp_path / ".claude" / "skills" / "my-skill" / "SKILL.md"
        assert skill_link.exists(), (
            "On re-init with declared packages, .claude/skills/my-skill/SKILL.md was not created"
        )
