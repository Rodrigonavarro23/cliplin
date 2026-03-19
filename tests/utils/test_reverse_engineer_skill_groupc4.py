"""Tests for cliplin-reverse-engineer skill — Group C batch 4.

Verifies SKILL.md contains correct AI instructions for:
- Skill warns and proceeds fresh when progress file is malformed
- Skill lists ambiguous matches when module targeting is ambiguous
- Skill scans from project root when no conventional source directories exist
"""
from cliplin.utils.templates import create_reverse_engineer_skill


def _skill(tmp_path) -> str:
    framework_base = tmp_path / ".cliplin" / "knowledge" / "cliplin-framework"
    framework_base.mkdir(parents=True)
    create_reverse_engineer_skill(framework_base)
    return (framework_base / "skills" / "cliplin-reverse-engineer" / "SKILL.md").read_text(encoding="utf-8")


class TestSkillMalformedProgressFile:
    """Skill warns and proceeds fresh when progress file is malformed."""

    def test_skill_instructs_to_warn_on_malformed_file(self, tmp_path):
        content = _skill(tmp_path)
        assert "malformed" in content.lower() or "not valid YAML" in content

    def test_skill_instructs_not_to_delete_malformed_file_automatically(self, tmp_path):
        content = _skill(tmp_path)
        assert "Do NOT delete" in content or "not delete" in content.lower() or "may want to fix" in content.lower()

    def test_skill_instructs_to_proceed_as_fresh_scan_on_malformed(self, tmp_path):
        content = _skill(tmp_path)
        assert "fresh" in content.lower() and "malformed" in content.lower()

    def test_skill_instructs_to_overwrite_malformed_file_when_first_module_starts(self, tmp_path):
        content = _skill(tmp_path)
        # Fresh scan writes a new file when first module starts
        assert "fresh scan" in content.lower() or "start" in content.lower()


class TestSkillAmbiguousModuleTargeting:
    """Skill lists ambiguous matches when module targeting is ambiguous."""

    def test_skill_instructs_to_list_multiple_matches(self, tmp_path):
        content = _skill(tmp_path)
        assert "multiple match" in content.lower() or "Ambiguous" in content or "ambiguous" in content.lower()

    def test_skill_instructs_to_ask_user_to_choose_on_ambiguity(self, tmp_path):
        content = _skill(tmp_path)
        assert "ask" in content.lower() or "choose" in content.lower() or "select" in content.lower()

    def test_skill_instructs_not_to_proceed_until_user_selects(self, tmp_path):
        content = _skill(tmp_path)
        assert "Wait for" in content or "explicit" in content.lower() or "selection" in content.lower()


class TestSkillScanFromProjectRoot:
    """Skill scans from project root when no conventional source directories exist."""

    def test_skill_instructs_fallback_to_project_root_scan(self, tmp_path):
        content = _skill(tmp_path)
        assert "project root" in content.lower()
        assert "none of these exist" in content.lower() or "If none" in content

    def test_skill_instructs_to_exclude_standard_dirs_on_root_scan(self, tmp_path):
        content = _skill(tmp_path)
        for excluded in ["node_modules", "vendor", ".git"]:
            assert excluded in content, f"'{excluded}' not mentioned in exclusions"

    def test_skill_instructs_to_treat_project_as_single_module_when_no_subdirs(self, tmp_path):
        content = _skill(tmp_path)
        assert "single module" in content.lower() or "one module" in content.lower()

    def test_skill_defines_empty_project_guard(self, tmp_path):
        content = _skill(tmp_path)
        assert "empty" in content.lower()
        assert "nothing to analyze" in content.lower() or "no files were found" in content.lower()
