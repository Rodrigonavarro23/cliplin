"""Tests for cliplin init --ai opencode integration.

Covers scenarios from docs/features/cli.feature:
  - "Initialize a Cliplin project with specific AI tool (OpenCode AI)"
  - "Initialize OpenCode AI in a directory with an existing opencode.json"
"""
import json
import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from cliplin.utils.ai_host_integrations.opencode import OpenCodeIntegration
from cliplin.utils.ai_host_integrations import get_known_ai_tool_ids, get_integration


class TestOpenCodeIntegrationRegistration:
    """Registry and id checks."""

    def test_opencode_is_known_tool_id(self):
        assert "opencode" in get_known_ai_tool_ids()

    def test_get_integration_returns_opencode_handler(self):
        integration = get_integration("opencode")
        assert integration is not None
        assert integration.id == "opencode"

    def test_opencode_mcp_config_path(self):
        integration = get_integration("opencode")
        assert integration.mcp_config_path == "opencode.json"

    def test_opencode_rules_dir(self):
        integration = get_integration("opencode")
        assert integration.rules_dir == "."


class TestOpenCodeApply:
    """Tests for OpenCodeIntegration.apply() on a clean directory."""

    def test_creates_opencode_json(self, tmp_path):
        OpenCodeIntegration().apply(tmp_path)
        config_file = tmp_path / "opencode.json"
        assert config_file.exists()

    def test_opencode_json_has_mcp_cliplin_context(self, tmp_path):
        OpenCodeIntegration().apply(tmp_path)
        config = json.loads((tmp_path / "opencode.json").read_text(encoding="utf-8"))
        assert "mcp" in config
        assert "cliplin-context" in config["mcp"]

    def test_mcp_type_is_local(self, tmp_path):
        OpenCodeIntegration().apply(tmp_path)
        config = json.loads((tmp_path / "opencode.json").read_text(encoding="utf-8"))
        server = config["mcp"]["cliplin-context"]
        assert server["type"] == "local"

    def test_mcp_command_is_array_with_uv_run_cliplin_mcp(self, tmp_path):
        OpenCodeIntegration().apply(tmp_path)
        config = json.loads((tmp_path / "opencode.json").read_text(encoding="utf-8"))
        server = config["mcp"]["cliplin-context"]
        assert server["command"] == ["uv", "run", "cliplin", "mcp"]

    def test_creates_opencode_md(self, tmp_path):
        OpenCodeIntegration().apply(tmp_path)
        md_file = tmp_path / "OPENCODE.md"
        assert md_file.exists()
        content = md_file.read_text(encoding="utf-8")
        assert len(content) > 100

    def test_opencode_md_has_cliplin_rules(self, tmp_path):
        OpenCodeIntegration().apply(tmp_path)
        content = (tmp_path / "OPENCODE.md").read_text(encoding="utf-8")
        assert "cliplin" in content.lower() or "context" in content.lower()

    def test_opencode_json_instructions_includes_opencode_md(self, tmp_path):
        OpenCodeIntegration().apply(tmp_path)
        config = json.loads((tmp_path / "opencode.json").read_text(encoding="utf-8"))
        assert "instructions" in config
        assert "OPENCODE.md" in config["instructions"]


class TestOpenCodeMerge:
    """Tests for merge behaviour when opencode.json already exists."""

    def test_preserves_existing_mcp_servers(self, tmp_path):
        existing = {
            "mcp": {
                "other-server": {"type": "local", "command": ["npx", "other-mcp"]}
            }
        }
        (tmp_path / "opencode.json").write_text(
            json.dumps(existing), encoding="utf-8"
        )
        OpenCodeIntegration().apply(tmp_path)
        config = json.loads((tmp_path / "opencode.json").read_text(encoding="utf-8"))
        assert "other-server" in config["mcp"]
        assert "cliplin-context" in config["mcp"]

    def test_preserves_existing_instructions(self, tmp_path):
        existing = {"instructions": ["CONTRIBUTING.md", "docs/guidelines.md"]}
        (tmp_path / "opencode.json").write_text(
            json.dumps(existing), encoding="utf-8"
        )
        OpenCodeIntegration().apply(tmp_path)
        config = json.loads((tmp_path / "opencode.json").read_text(encoding="utf-8"))
        assert "CONTRIBUTING.md" in config["instructions"]
        assert "docs/guidelines.md" in config["instructions"]
        assert "OPENCODE.md" in config["instructions"]

    def test_does_not_duplicate_opencode_md_in_instructions(self, tmp_path):
        existing = {"instructions": ["OPENCODE.md", "other.md"]}
        (tmp_path / "opencode.json").write_text(
            json.dumps(existing), encoding="utf-8"
        )
        OpenCodeIntegration().apply(tmp_path)
        config = json.loads((tmp_path / "opencode.json").read_text(encoding="utf-8"))
        assert config["instructions"].count("OPENCODE.md") == 1

    def test_preserves_other_settings(self, tmp_path):
        existing = {"$schema": "https://opencode.ai/config.json", "model": "gpt-4"}
        (tmp_path / "opencode.json").write_text(
            json.dumps(existing), encoding="utf-8"
        )
        OpenCodeIntegration().apply(tmp_path)
        config = json.loads((tmp_path / "opencode.json").read_text(encoding="utf-8"))
        assert config.get("$schema") == "https://opencode.ai/config.json"
        assert config.get("model") == "gpt-4"

    def test_handles_invalid_json_gracefully(self, tmp_path):
        (tmp_path / "opencode.json").write_text("not valid json", encoding="utf-8")
        # Should not raise — falls back to creating fresh config
        OpenCodeIntegration().apply(tmp_path)
        config = json.loads((tmp_path / "opencode.json").read_text(encoding="utf-8"))
        assert "mcp" in config


class TestOpenCodeSkillLinking:
    """Tests for .opencode/skills/ skill linking."""

    def test_links_skills_from_framework_package(self, tmp_path):
        framework_base = tmp_path / ".cliplin" / "knowledge" / "cliplin-framework"
        skill_dir = framework_base / "skills" / "my-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# My Skill", encoding="utf-8")

        integration = OpenCodeIntegration()
        integration.link_knowledge_skills(tmp_path, framework_base)

        linked = tmp_path / ".opencode" / "skills" / "my-skill" / "SKILL.md"
        assert linked.exists()
        assert linked.read_text(encoding="utf-8") == "# My Skill"

    def test_skill_link_failure_does_not_raise(self, tmp_path):
        framework_base = tmp_path / ".cliplin" / "knowledge" / "cliplin-framework"
        skill_dir = framework_base / "skills" / "my-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# My Skill", encoding="utf-8")

        integration = OpenCodeIntegration()
        with patch("os.link", side_effect=OSError("cross-device")):
            # Should warn but not raise
            integration.link_knowledge_skills(tmp_path, framework_base)

    def test_no_skills_src_dir_is_noop(self, tmp_path):
        framework_base = tmp_path / ".cliplin" / "knowledge" / "cliplin-framework"
        framework_base.mkdir(parents=True)
        # No skills/ subdirectory
        integration = OpenCodeIntegration()
        integration.link_knowledge_skills(tmp_path, framework_base)
        assert not (tmp_path / ".opencode" / "skills").exists()

    def test_reinit_refreshes_skill_link(self, tmp_path):
        framework_base = tmp_path / ".cliplin" / "knowledge" / "cliplin-framework"
        skill_dir = framework_base / "skills" / "my-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("v1", encoding="utf-8")

        integration = OpenCodeIntegration()
        integration.link_knowledge_skills(tmp_path, framework_base)

        # Update skill content and re-link
        (skill_dir / "SKILL.md").write_text("v2", encoding="utf-8")
        integration.link_knowledge_skills(tmp_path, framework_base)

        linked = tmp_path / ".opencode" / "skills" / "my-skill" / "SKILL.md"
        assert linked.read_text(encoding="utf-8") == "v2"
