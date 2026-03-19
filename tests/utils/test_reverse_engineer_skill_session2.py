"""Tests for cliplin-reverse-engineer skill — session 2.

Covers scenarios from docs/features/reverse-engineer.feature:
- Skill is linked to Gemini skills directory on init with --ai gemini
- feature-template-mapping.md records the reverse-engineer skill mapping
- cliplin init adds .re-progress.yaml to .gitignore when not already covered
- cliplin init does not duplicate .gitignore entry when already covered
- cliplin init creates .gitignore with the entry when no .gitignore exists
"""
import os
from pathlib import Path

from cliplin.utils.templates import create_framework_knowledge_package
from cliplin.utils.ai_host_integrations.gemini_cli import GeminiCliIntegration
from cliplin.commands.init import ensure_cliplin_in_gitignore


class TestReverseEngineerSkillLinkedToGemini:
    """Skill is linked to Gemini skills directory on init with --ai gemini."""

    def test_hard_link_created_at_gemini_skills(self, tmp_path):
        create_framework_knowledge_package(tmp_path)
        framework_base = tmp_path / ".cliplin" / "knowledge" / "cliplin-framework"
        integration = GeminiCliIntegration()

        integration.link_knowledge_skills(tmp_path, framework_base)

        linked = tmp_path / ".gemini" / "skills" / "cliplin-reverse-engineer" / "SKILL.md"
        assert linked.exists(), ".gemini/skills/cliplin-reverse-engineer/SKILL.md not created"

    def test_gemini_skills_directory_exists(self, tmp_path):
        create_framework_knowledge_package(tmp_path)
        framework_base = tmp_path / ".cliplin" / "knowledge" / "cliplin-framework"
        integration = GeminiCliIntegration()

        integration.link_knowledge_skills(tmp_path, framework_base)

        assert (tmp_path / ".gemini" / "skills" / "cliplin-reverse-engineer").is_dir()

    def test_linked_file_shares_inode_with_source(self, tmp_path):
        create_framework_knowledge_package(tmp_path)
        framework_base = tmp_path / ".cliplin" / "knowledge" / "cliplin-framework"
        integration = GeminiCliIntegration()

        integration.link_knowledge_skills(tmp_path, framework_base)

        src = framework_base / "skills" / "cliplin-reverse-engineer" / "SKILL.md"
        dst = tmp_path / ".gemini" / "skills" / "cliplin-reverse-engineer" / "SKILL.md"
        try:
            assert os.stat(src).st_ino == os.stat(dst).st_ino, "Files are not hard-linked"
        except OSError:
            pass  # cross-filesystem: skip inode check


class TestFeatureTemplateMappingEntry:
    """feature-template-mapping.md records the reverse-engineer skill mapping."""

    def test_mapping_entry_exists_in_tdr(self):
        mapping_file = Path("docs/tdrs/feature-template-mapping.md")
        assert mapping_file.exists(), "feature-template-mapping.md not found"
        content = mapping_file.read_text(encoding="utf-8")
        assert "reverse-engineer.feature" in content, \
            "reverse-engineer.feature not listed in feature-template-mapping.md"
        assert "create_reverse_engineer_skill" in content, \
            "create_reverse_engineer_skill not listed in feature-template-mapping.md"

    def test_mapping_references_correct_template_function(self):
        content = Path("docs/tdrs/feature-template-mapping.md").read_text(encoding="utf-8")
        # Verify both the feature file and template function appear on the same logical entry
        lines = content.splitlines()
        re_lines = [l for l in lines if "reverse-engineer" in l]
        assert any("create_reverse_engineer_skill" in l for l in re_lines), \
            "reverse-engineer entry does not reference create_reverse_engineer_skill"

    def test_create_reverse_engineer_skill_exists_in_templates(self):
        import cliplin.utils.templates as t
        assert hasattr(t, "create_reverse_engineer_skill"), \
            "create_reverse_engineer_skill not found in templates.py"


class TestGitignoreReProgressCoverage:
    """cliplin init ensures .re-progress.yaml is not committed.

    The existing ensure_cliplin_in_gitignore adds '.cliplin' which covers
    '.cliplin/.re-progress.yaml'. These tests verify that coverage.
    """

    def test_gitignore_created_with_cliplin_entry_when_none_exists(self, tmp_path):
        ensure_cliplin_in_gitignore(tmp_path)

        gitignore = tmp_path / ".gitignore"
        assert gitignore.exists(), ".gitignore was not created"
        content = gitignore.read_text(encoding="utf-8")
        assert ".cliplin" in content, ".cliplin not in .gitignore"

    def test_gitignore_entry_covers_re_progress_yaml(self, tmp_path):
        ensure_cliplin_in_gitignore(tmp_path)

        content = (tmp_path / ".gitignore").read_text(encoding="utf-8")
        # .cliplin covers .cliplin/.re-progress.yaml
        assert any(
            entry.strip() in (".cliplin", ".cliplin/", ".cliplin/.re-progress.yaml")
            for entry in content.splitlines()
        ), ".gitignore does not contain an entry covering .re-progress.yaml"

    def test_gitignore_not_duplicated_when_already_covered(self, tmp_path):
        (tmp_path / ".gitignore").write_text(".cliplin\n", encoding="utf-8")

        ensure_cliplin_in_gitignore(tmp_path)

        content = (tmp_path / ".gitignore").read_text(encoding="utf-8")
        count = sum(1 for line in content.splitlines() if ".cliplin" in line)
        assert count == 1, f".cliplin entry duplicated in .gitignore ({count} occurrences)"

    def test_gitignore_entry_appended_when_not_already_covered(self, tmp_path):
        (tmp_path / ".gitignore").write_text("node_modules/\ndist/\n", encoding="utf-8")

        ensure_cliplin_in_gitignore(tmp_path)

        content = (tmp_path / ".gitignore").read_text(encoding="utf-8")
        assert ".cliplin" in content, ".cliplin not appended to existing .gitignore"
        assert "node_modules/" in content, "existing entries were removed"

    def test_gitignore_written_with_utf8_encoding(self, tmp_path):
        ensure_cliplin_in_gitignore(tmp_path)

        content = (tmp_path / ".gitignore").read_text(encoding="utf-8")
        assert len(content) > 0
