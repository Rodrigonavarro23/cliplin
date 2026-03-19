"""Tests for cliplin-reverse-engineer skill — Group C batch 2.

Verifies SKILL.md contains correct AI instructions for:
- Skill proposes spec drafts one by one in Phase 2 and waits for confirmation
- Skill writes and updates the tracking file during execution
- Skill offers to resume when a progress file is found on re-invocation
"""
from cliplin.utils.templates import create_reverse_engineer_skill


def _skill(tmp_path) -> str:
    framework_base = tmp_path / ".cliplin" / "knowledge" / "cliplin-framework"
    framework_base.mkdir(parents=True)
    create_reverse_engineer_skill(framework_base)
    return (framework_base / "skills" / "cliplin-reverse-engineer" / "SKILL.md").read_text(encoding="utf-8")


class TestSkillPhase2GuidedDrafting:
    """Skill proposes spec drafts one by one in Phase 2 and waits for confirmation."""

    def test_skill_instructs_to_propose_draft_per_finding(self, tmp_path):
        content = _skill(tmp_path)
        assert "AGENT PROPOSAL" in content

    def test_skill_instructs_to_wait_for_confirmation_before_next_finding(self, tmp_path):
        content = _skill(tmp_path)
        assert "Wait for human confirmation" in content or "wait for" in content.lower()

    def test_skill_instructs_to_propose_one_finding_at_a_time(self, tmp_path):
        content = _skill(tmp_path)
        assert "in sequence" in content or "one at a time" in content.lower() or "For each finding" in content

    def test_skill_instructs_to_run_cliplin_reindex_after_approval(self, tmp_path):
        content = _skill(tmp_path)
        assert "cliplin reindex" in content

    def test_skill_instructs_to_ask_move_to_next_module_after_phase2(self, tmp_path):
        content = _skill(tmp_path)
        assert "Move to next module" in content


class TestSkillTrackingFile:
    """Skill writes and updates the tracking file during execution."""

    def test_skill_defines_tracking_file_path(self, tmp_path):
        content = _skill(tmp_path)
        assert ".cliplin/.re-progress.yaml" in content

    def test_skill_defines_modules_completed_field(self, tmp_path):
        content = _skill(tmp_path)
        assert "modules_completed" in content

    def test_skill_defines_modules_pending_field(self, tmp_path):
        content = _skill(tmp_path)
        assert "modules_pending" in content

    def test_skill_defines_current_module_field(self, tmp_path):
        content = _skill(tmp_path)
        assert "current_module" in content

    def test_skill_defines_current_phase_field(self, tmp_path):
        content = _skill(tmp_path)
        assert "current_phase" in content

    def test_skill_defines_context_references_field(self, tmp_path):
        content = _skill(tmp_path)
        assert "context_references" in content

    def test_skill_instructs_to_update_file_after_each_phase(self, tmp_path):
        content = _skill(tmp_path)
        assert "Write/update" in content or "update" in content.lower()

    def test_skill_instructs_not_to_commit_progress_file(self, tmp_path):
        content = _skill(tmp_path)
        assert "Do NOT commit" in content or "not commit" in content.lower() or "gitignore" in content.lower()

    def test_skill_defines_generated_at_field(self, tmp_path):
        content = _skill(tmp_path)
        assert "generated_at" in content

    def test_skill_defines_modules_total_field(self, tmp_path):
        content = _skill(tmp_path)
        assert "modules_total" in content


class TestSkillResumeOnReInvocation:
    """Skill offers to resume when a progress file is found on re-invocation."""

    def test_skill_instructs_to_check_for_progress_file_on_startup(self, tmp_path):
        content = _skill(tmp_path)
        assert "startup" in content.lower() or "Before you start" in content or "startup check" in content.lower()

    def test_skill_instructs_to_show_resume_options(self, tmp_path):
        content = _skill(tmp_path)
        assert "[C]" in content
        assert "[R]" in content
        assert "[M]" in content

    def test_skill_instructs_to_reload_mcp_context_on_continue(self, tmp_path):
        content = _skill(tmp_path)
        assert "context_references" in content
        assert "reload" in content.lower() or "re-issue" in content.lower() or "reload" in content.lower()

    def test_skill_instructs_to_delete_progress_file_on_restart(self, tmp_path):
        content = _skill(tmp_path)
        assert "delete" in content.lower() or "Delete" in content

    def test_skill_instructs_not_to_scan_before_user_chooses(self, tmp_path):
        content = _skill(tmp_path)
        assert "Wait for explicit user choice" in content or "wait for" in content.lower()

    def test_skill_handles_malformed_progress_file(self, tmp_path):
        content = _skill(tmp_path)
        assert "malformed" in content.lower() or "not valid YAML" in content or "invalid" in content.lower()
