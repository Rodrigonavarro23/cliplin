"""Tests for cliplin-reverse-engineer skill — Group C batch 1.

Verifies that SKILL.md contains the correct AI instructions for:
- Skill detects top-level modules from source tree
- Skill presents a process plan and waits for confirmation before proceeding
- Skill produces a findings report (Phase 1) for a module
"""
from pathlib import Path

from cliplin.utils.templates import create_reverse_engineer_skill


def _get_skill_content(tmp_path) -> str:
    framework_base = tmp_path / ".cliplin" / "knowledge" / "cliplin-framework"
    framework_base.mkdir(parents=True)
    create_reverse_engineer_skill(framework_base)
    return (framework_base / "skills" / "cliplin-reverse-engineer" / "SKILL.md").read_text(encoding="utf-8")


class TestSkillDetectsTopLevelModules:
    """Skill detects top-level modules from source tree."""

    def test_skill_instructs_to_list_immediate_subdirectories(self, tmp_path):
        content = _get_skill_content(tmp_path)
        assert "immediate subdirector" in content.lower()

    def test_skill_defines_module_name_field(self, tmp_path):
        content = _get_skill_content(tmp_path)
        assert "module_name" in content

    def test_skill_defines_inferred_domain_field(self, tmp_path):
        content = _get_skill_content(tmp_path)
        assert "inferred_domain" in content

    def test_skill_defines_has_existing_specs_field(self, tmp_path):
        content = _get_skill_content(tmp_path)
        assert "has_existing_specs" in content

    def test_skill_instructs_to_cross_reference_with_existing_feature_files(self, tmp_path):
        content = _get_skill_content(tmp_path)
        assert "governed_by" in content or "existing feature" in content.lower()

    def test_skill_covers_conventional_source_roots(self, tmp_path):
        content = _get_skill_content(tmp_path)
        for root in ["src/", "lib/", "app/"]:
            assert root in content, f"source root '{root}' not mentioned in SKILL.md"


class TestSkillProcessPlan:
    """Skill presents a process plan and waits for confirmation before proceeding."""

    def test_skill_instructs_to_list_modules_with_coverage_status(self, tmp_path):
        content = _get_skill_content(tmp_path)
        assert "coverage" in content.lower()
        assert "existing" in content or "partial" in content or "none" in content

    def test_skill_instructs_to_ask_confirmation_before_starting(self, tmp_path):
        content = _get_skill_content(tmp_path)
        assert "Shall I start" in content or "confirm" in content.lower()

    def test_skill_instructs_not_to_proceed_without_confirmation(self, tmp_path):
        content = _get_skill_content(tmp_path)
        assert "explicit confirmation" in content.lower() or "Do NOT proceed" in content or "only after" in content.lower()

    def test_skill_instructs_to_write_progress_file_after_plan(self, tmp_path):
        content = _get_skill_content(tmp_path)
        assert ".re-progress.yaml" in content

    def test_skill_shows_phase_labels_in_plan(self, tmp_path):
        content = _get_skill_content(tmp_path)
        assert "Phase 1" in content
        assert "Phase 2" in content


class TestSkillPhase1FindingsReport:
    """Skill produces a findings report (Phase 1) for a module."""

    def test_skill_instructs_to_report_domain_concepts(self, tmp_path):
        content = _get_skill_content(tmp_path)
        assert "domain concept" in content.lower() or "Detected domain" in content

    def test_skill_instructs_to_report_inferred_use_cases(self, tmp_path):
        content = _get_skill_content(tmp_path)
        assert "use case" in content.lower() or "Inferred use" in content

    def test_skill_instructs_to_report_existing_coverage(self, tmp_path):
        content = _get_skill_content(tmp_path)
        assert "Existing coverage" in content or "existing coverage" in content.lower()

    def test_skill_defines_missing_feature_finding_type(self, tmp_path):
        content = _get_skill_content(tmp_path)
        assert "[MISSING-FEATURE]" in content

    def test_skill_defines_missing_tdr_finding_type(self, tmp_path):
        content = _get_skill_content(tmp_path)
        assert "[MISSING-TDR]" in content

    def test_skill_defines_missing_adr_finding_type(self, tmp_path):
        content = _get_skill_content(tmp_path)
        assert "[MISSING-ADR]" in content

    def test_skill_defines_missing_business_doc_finding_type(self, tmp_path):
        content = _get_skill_content(tmp_path)
        assert "[MISSING-BUSINESS-DOC]" in content

    def test_skill_defines_partial_spec_finding_type(self, tmp_path):
        content = _get_skill_content(tmp_path)
        assert "[PARTIAL-SPEC]" in content

    def test_skill_instructs_to_include_context_signals_beyond_code(self, tmp_path):
        content = _get_skill_content(tmp_path)
        assert "Context signals beyond code" in content or "beyond code" in content.lower()

    def test_skill_instructs_to_ask_before_starting_phase2(self, tmp_path):
        content = _get_skill_content(tmp_path)
        assert "Proceed to Phase 2" in content

    def test_skill_instructs_to_update_progress_file_after_phase1(self, tmp_path):
        content = _get_skill_content(tmp_path)
        assert "current_phase" in content
