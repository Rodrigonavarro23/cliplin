"""Tests for cliplin init --ai wibey integration.

Covers scenarios from docs/features/cli.feature:
  - "Initialize a Cliplin project with specific AI tool (Wibey)"
  - "Initialize Wibey in a directory with an existing AGENTS.md from another host"
"""
import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from cliplin.utils.ai_host_integrations import get_integration, get_known_ai_tool_ids
from cliplin.utils.ai_host_integrations.wibey import WibeyIntegration


class TestWibeyIntegrationRegistration:
    def test_wibey_is_known_tool_id(self):
        assert "wibey" in get_known_ai_tool_ids()

    def test_get_integration_returns_wibey_handler(self):
        integration = get_integration("wibey")
        assert integration is not None
        assert integration.id == "wibey"

    def test_wibey_mcp_config_path(self):
        assert get_integration("wibey").mcp_config_path == ".wibey/mcp.json"

    def test_wibey_rules_dir(self):
        assert get_integration("wibey").rules_dir == ".wibey/rules"


class TestWibeyApply:
    def test_creates_wibey_directory(self, tmp_path):
        WibeyIntegration().apply(tmp_path)
        assert (tmp_path / ".wibey").is_dir()

    def test_creates_wibey_mcp_json(self, tmp_path):
        WibeyIntegration().apply(tmp_path)
        assert (tmp_path / ".wibey" / "mcp.json").exists()

    def test_mcp_json_has_cliplin_context(self, tmp_path):
        WibeyIntegration().apply(tmp_path)
        config = json.loads((tmp_path / ".wibey" / "mcp.json").read_text(encoding="utf-8"))
        assert "mcpServers" in config
        assert "cliplin-context" in config["mcpServers"]

    def test_mcp_command_and_args(self, tmp_path):
        WibeyIntegration().apply(tmp_path)
        server = json.loads(
            (tmp_path / ".wibey" / "mcp.json").read_text(encoding="utf-8")
        )["mcpServers"]["cliplin-context"]
        assert server["command"] == "uv"
        assert server["args"] == ["run", "cliplin", "mcp"]

    def test_creates_rules_directory(self, tmp_path):
        WibeyIntegration().apply(tmp_path)
        assert (tmp_path / ".wibey" / "rules").is_dir()

    def test_creates_all_rule_files(self, tmp_path):
        WibeyIntegration().apply(tmp_path)
        rules_dir = tmp_path / ".wibey" / "rules"
        for name in [
            "context.md",
            "feature-first-flow.md",
            "feature-processing.md",
            "context-protocol-loading.md",
        ]:
            assert (rules_dir / name).exists(), f"Missing rule file: {name}"

    def test_rule_files_have_content(self, tmp_path):
        WibeyIntegration().apply(tmp_path)
        for name in [
            "context.md",
            "feature-first-flow.md",
            "feature-processing.md",
            "context-protocol-loading.md",
        ]:
            content = (tmp_path / ".wibey" / "rules" / name).read_text(encoding="utf-8")
            assert len(content) > 50

    def test_creates_instructions_md(self, tmp_path):
        WibeyIntegration().apply(tmp_path)
        assert (tmp_path / ".wibey" / "instructions.md").exists()

    def test_instructions_md_has_full_rule_content(self, tmp_path):
        WibeyIntegration().apply(tmp_path)
        content = (tmp_path / ".wibey" / "instructions.md").read_text(encoding="utf-8")
        assert len(content) > 2000
        assert "context" in content.lower()

    def test_creates_agents_md(self, tmp_path):
        WibeyIntegration().apply(tmp_path)
        assert (tmp_path / "AGENTS.md").exists()

    def test_agents_md_has_section_markers(self, tmp_path):
        WibeyIntegration().apply(tmp_path)
        content = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
        assert "<!-- cliplin-wibey-start -->" in content
        assert "<!-- cliplin-wibey-end -->" in content

    def test_agents_md_contains_imperative_instruction(self, tmp_path):
        WibeyIntegration().apply(tmp_path)
        content = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
        assert "MUST" in content or "must" in content

    def test_agents_md_mentions_always_apply(self, tmp_path):
        WibeyIntegration().apply(tmp_path)
        content = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
        assert "alwaysApply" in content

    def test_agents_md_mentions_before_any_interaction(self, tmp_path):
        WibeyIntegration().apply(tmp_path)
        content = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
        lower = content.lower()
        assert "before" in lower and ("interaction" in lower or "request" in lower)

    def test_agents_md_cliplin_section_is_under_2000_chars(self, tmp_path):
        WibeyIntegration().apply(tmp_path)
        content = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
        start = content.index("<!-- cliplin-wibey-start -->")
        end = content.index("<!-- cliplin-wibey-end -->") + len("<!-- cliplin-wibey-end -->")
        assert (end - start) < 2000

    def test_agents_md_lists_instructions_md_path(self, tmp_path):
        WibeyIntegration().apply(tmp_path)
        content = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
        assert ".wibey/instructions.md" in content

    def test_agents_md_lists_rule_file_paths(self, tmp_path):
        WibeyIntegration().apply(tmp_path)
        content = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
        for rule in ["context.md", "feature-first-flow.md", "feature-processing.md", "context-protocol-loading.md"]:
            assert f".wibey/rules/{rule}" in content


class TestWibeyMcpMerge:
    """Merge behaviour when .wibey/mcp.json already exists."""

    def test_preserves_existing_mcp_servers(self, tmp_path):
        (tmp_path / ".wibey").mkdir()
        existing = {"mcpServers": {"other-server": {"command": "node", "args": ["other.js"]}}}
        (tmp_path / ".wibey" / "mcp.json").write_text(json.dumps(existing), encoding="utf-8")
        WibeyIntegration().apply(tmp_path)
        config = json.loads((tmp_path / ".wibey" / "mcp.json").read_text(encoding="utf-8"))
        assert "other-server" in config["mcpServers"]
        assert "cliplin-context" in config["mcpServers"]

    def test_handles_invalid_json_gracefully(self, tmp_path):
        (tmp_path / ".wibey").mkdir()
        (tmp_path / ".wibey" / "mcp.json").write_text("not valid json", encoding="utf-8")
        WibeyIntegration().apply(tmp_path)
        config = json.loads((tmp_path / ".wibey" / "mcp.json").read_text(encoding="utf-8"))
        assert "mcpServers" in config


class TestWibeyAgentsMdMerge:
    """Multi-host AGENTS.md merge behaviour."""

    def test_preserves_foreign_content_before_cliplin_section(self, tmp_path):
        existing = "# Other Tool Instructions\n\nSome other tool's rules.\n"
        (tmp_path / "AGENTS.md").write_text(existing, encoding="utf-8")
        WibeyIntegration().apply(tmp_path)
        content = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
        assert "Other Tool Instructions" in content
        assert "Some other tool's rules." in content

    def test_appends_cliplin_section_when_markers_absent(self, tmp_path):
        (tmp_path / "AGENTS.md").write_text("# Other Tool\n\nContent.\n", encoding="utf-8")
        WibeyIntegration().apply(tmp_path)
        content = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
        assert "<!-- cliplin-wibey-start -->" in content
        assert "<!-- cliplin-wibey-end -->" in content

    def test_updates_existing_cliplin_section_no_duplicate(self, tmp_path):
        WibeyIntegration().apply(tmp_path)
        WibeyIntegration().apply(tmp_path)
        content = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
        assert content.count("<!-- cliplin-wibey-start -->") == 1
        assert content.count("<!-- cliplin-wibey-end -->") == 1

    def test_preserves_content_after_cliplin_section(self, tmp_path):
        from cliplin.utils.templates import get_wibey_agents_md_content
        existing = (
            "# Before\n\n"
            + get_wibey_agents_md_content()
            + "\n# After\n\nContent after cliplin.\n"
        )
        (tmp_path / "AGENTS.md").write_text(existing, encoding="utf-8")
        WibeyIntegration().apply(tmp_path)
        content = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
        assert "# Before" in content
        assert "# After" in content
        assert "Content after cliplin." in content

    def test_does_not_remove_other_sections(self, tmp_path):
        existing = "# Cursor Rules\n\nCursor-specific stuff.\n"
        (tmp_path / "AGENTS.md").write_text(existing, encoding="utf-8")
        WibeyIntegration().apply(tmp_path)
        content = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
        assert "Cursor Rules" in content
        assert "Cursor-specific stuff." in content


class TestWibeySkillLinking:
    def test_links_skills_from_framework_package(self, tmp_path):
        framework_base = tmp_path / ".cliplin" / "knowledge" / "cliplin-framework"
        skill_dir = framework_base / "skills" / "my-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# My Skill", encoding="utf-8")

        WibeyIntegration().link_knowledge_skills(tmp_path, framework_base)

        linked = tmp_path / ".wibey" / "skills" / "my-skill" / "SKILL.md"
        assert linked.exists()
        assert linked.read_text(encoding="utf-8") == "# My Skill"

    def test_skill_link_failure_does_not_raise(self, tmp_path):
        framework_base = tmp_path / ".cliplin" / "knowledge" / "cliplin-framework"
        skill_dir = framework_base / "skills" / "my-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# My Skill", encoding="utf-8")

        with patch("os.link", side_effect=OSError("cross-device")):
            WibeyIntegration().link_knowledge_skills(tmp_path, framework_base)

    def test_no_skills_src_is_noop(self, tmp_path):
        framework_base = tmp_path / ".cliplin" / "knowledge" / "cliplin-framework"
        framework_base.mkdir(parents=True)
        WibeyIntegration().link_knowledge_skills(tmp_path, framework_base)
        assert not (tmp_path / ".wibey" / "skills").exists()

    def test_reinit_refreshes_skill_link(self, tmp_path):
        framework_base = tmp_path / ".cliplin" / "knowledge" / "cliplin-framework"
        skill_dir = framework_base / "skills" / "my-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("v1", encoding="utf-8")

        integration = WibeyIntegration()
        integration.link_knowledge_skills(tmp_path, framework_base)
        (skill_dir / "SKILL.md").write_text("v2", encoding="utf-8")
        integration.link_knowledge_skills(tmp_path, framework_base)

        linked = tmp_path / ".wibey" / "skills" / "my-skill" / "SKILL.md"
        assert linked.read_text(encoding="utf-8") == "v2"
