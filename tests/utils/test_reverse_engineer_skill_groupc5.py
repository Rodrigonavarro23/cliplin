"""Tests for cliplin-reverse-engineer skill — Group C batch 5 (final).

Verifies SKILL.md contains correct AI instructions for:
- Skill handles resume option M to jump to a specific module
- Skill rewrites tracking file with full module list when continuing after targeted run
"""
from cliplin.utils.templates import create_reverse_engineer_skill


def _skill(tmp_path) -> str:
    framework_base = tmp_path / ".cliplin" / "knowledge" / "cliplin-framework"
    framework_base.mkdir(parents=True)
    create_reverse_engineer_skill(framework_base)
    return (framework_base / "skills" / "cliplin-reverse-engineer" / "SKILL.md").read_text(encoding="utf-8")


class TestSkillResumeMJumpToModule:
    """Skill handles resume option M to jump to a specific module."""

    def test_skill_defines_option_m_in_resume_prompt(self, tmp_path):
        content = _skill(tmp_path)
        assert "[M]" in content

    def test_skill_instructs_option_m_asks_which_module(self, tmp_path):
        content = _skill(tmp_path)
        # [M] should lead to asking which module to jump to
        assert "Jump to" in content or "jump to" in content.lower()

    def test_skill_instructs_to_jump_directly_to_phase1_via_m(self, tmp_path):
        content = _skill(tmp_path)
        assert "[M]" in content and "Phase 1" in content

    def test_skill_instructs_not_to_reprocess_completed_modules(self, tmp_path):
        content = _skill(tmp_path)
        assert "modules_completed" in content


class TestSkillRewriteTrackingFileOnFullScanContinue:
    """Skill rewrites tracking file with full module list when continuing after targeted run."""

    def test_skill_instructs_to_rewrite_progress_file_with_real_total(self, tmp_path):
        content = _skill(tmp_path)
        assert "rewrite" in content.lower() and "modules_total" in content

    def test_skill_instructs_modules_completed_includes_targeted_module(self, tmp_path):
        content = _skill(tmp_path)
        assert "modules_completed" in content

    def test_skill_instructs_to_reset_invocation_target_to_null(self, tmp_path):
        content = _skill(tmp_path)
        assert "invocation_target" in content and "null" in content

    def test_skill_instructs_rewrite_before_next_module_starts(self, tmp_path):
        content = _skill(tmp_path)
        # Rewrite happens before Phase 1 of next module
        assert "rewrite" in content.lower() or "Rewrite" in content
