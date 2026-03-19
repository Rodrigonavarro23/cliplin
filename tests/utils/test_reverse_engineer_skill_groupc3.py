"""Tests for cliplin-reverse-engineer skill — Group C batch 3.

Verifies SKILL.md contains correct AI instructions for:
- Skill targets a specific module when invoked with a module name
- Skill performs targeted scan when invoked on a module with no progress file
- Skill deletes the tracking file when all modules are complete
"""
from cliplin.utils.templates import create_reverse_engineer_skill


def _skill(tmp_path) -> str:
    framework_base = tmp_path / ".cliplin" / "knowledge" / "cliplin-framework"
    framework_base.mkdir(parents=True)
    create_reverse_engineer_skill(framework_base)
    return (framework_base / "skills" / "cliplin-reverse-engineer" / "SKILL.md").read_text(encoding="utf-8")


class TestSkillModuleTargetingWithProgressFile:
    """Skill targets a specific module when invoked with a module name (progress file exists)."""

    def test_skill_defines_module_targeting_section(self, tmp_path):
        content = _skill(tmp_path)
        assert "Module targeting" in content

    def test_skill_instructs_to_load_module_list_from_progress_file(self, tmp_path):
        content = _skill(tmp_path)
        assert "progress file" in content.lower() and "module" in content.lower()

    def test_skill_instructs_case_insensitive_partial_match(self, tmp_path):
        content = _skill(tmp_path)
        assert "case-insensitive" in content.lower() or "partial match" in content.lower()

    def test_skill_instructs_to_jump_to_phase1_for_targeted_module(self, tmp_path):
        content = _skill(tmp_path)
        assert "jump" in content.lower() and "Phase 1" in content

    def test_skill_instructs_to_ask_continue_full_scan_after_targeted_module(self, tmp_path):
        content = _skill(tmp_path)
        assert "continue with the full project scan" in content or "full scan" in content.lower()

    def test_skill_instructs_to_list_available_modules_on_no_match(self, tmp_path):
        content = _skill(tmp_path)
        assert "no match" in content.lower() or "list available modules" in content.lower() or "does not match" in content.lower()


class TestSkillTargetedScanWithoutProgressFile:
    """Skill performs targeted scan when invoked on a module with no progress file."""

    def test_skill_instructs_targeted_scan_of_specified_path(self, tmp_path):
        content = _skill(tmp_path)
        assert "targeted scan" in content.lower() or "scan only" in content.lower()

    def test_skill_instructs_to_skip_process_plan_for_targeted_invocation(self, tmp_path):
        content = _skill(tmp_path)
        assert "Skip the process plan" in content or "without showing a process plan" in content or "skip" in content.lower()

    def test_skill_instructs_to_set_modules_total_1_for_targeted_scan(self, tmp_path):
        content = _skill(tmp_path)
        assert "modules_total: 1" in content

    def test_skill_instructs_to_set_invocation_target_field(self, tmp_path):
        content = _skill(tmp_path)
        assert "invocation_target" in content

    def test_skill_instructs_to_rewrite_progress_file_on_full_scan_continue(self, tmp_path):
        content = _skill(tmp_path)
        assert "rewrite" in content.lower() or "rewriting" in content.lower()

    def test_skill_instructs_to_reset_invocation_target_to_null_on_full_scan(self, tmp_path):
        content = _skill(tmp_path)
        assert "invocation_target: null" in content or "reset to `null`" in content or 'null' in content


class TestSkillDeletesTrackingFileOnCompletion:
    """Skill deletes the tracking file when all modules are complete."""

    def test_skill_instructs_to_delete_progress_file_when_done(self, tmp_path):
        content = _skill(tmp_path)
        assert "delete" in content.lower() and ".re-progress.yaml" in content

    def test_skill_defines_completion_condition(self, tmp_path):
        content = _skill(tmp_path)
        assert "all modules" in content.lower() or "complete" in content.lower()

    def test_skill_instructs_deletion_after_last_module(self, tmp_path):
        content = _skill(tmp_path)
        # Should mention deleting file at completion
        assert "Delete" in content or "delete" in content
        assert "complete" in content.lower()
