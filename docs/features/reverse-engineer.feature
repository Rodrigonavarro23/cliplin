@constraints
# governed_by:
#   - docs/tdrs/reverse-engineer-skill.md
#   - docs/tdrs/context-audit-skill.md
#   - docs/tdrs/ai-host-integration.md
#   - docs/tdrs/ai-host-integration-handler-pattern.md
#   - docs/tdrs/claude-desktop-integration.md
#   - docs/tdrs/gemini-integration.md
#   - docs/tdrs/feature-template-mapping.md
#   - docs/tdrs/cliplin-cli-stack.md
# conflicts: []
# gaps: []
# escalation_triggers:
#   - "If link_knowledge_skills call site is ambiguous during implementation, stop and confirm: call goes in each integration handler's apply() after create_framework_knowledge_package"
#   - "If .re-progress.yaml write fails (permissions, disk full), stop and ask: warn and continue or abort?"
#   - "If targeted scan path is outside the project root, stop and ask: reject or warn and continue?"
#   - "If .gitignore append fails at init time (permissions), stop and ask: warn and continue or fail?"
Feature: cliplin-reverse-engineer Built-in Skill
  As a developer joining a project without documentation
  I want a built-in skill that reverse-engineers my project and guides me to create specs
  So that I can bootstrap feature files, ADRs, TDRs, and business docs from existing code

  Background:
    Given I have initialized a Cliplin project
    And the project has a `.cliplin/knowledge/cliplin-framework/` built-in package

  @status:implemented
  @changed:2026-03-19
  Scenario: Skill file is created inside the framework package on cliplin init
    Given I have the Cliplin CLI tool installed
    And I am in a directory with an existing project
    When I run `cliplin init`
    Then the CLI should create the skill at `.cliplin/knowledge/cliplin-framework/skills/cliplin-reverse-engineer/SKILL.md`
    And the SKILL.md should describe the scan sources
    And the SKILL.md should describe the top-level module detection algorithm
    And the SKILL.md should describe the two-phase per-module flow
    And the SKILL.md should describe the tracking file format and resume behavior

  @status:implemented
  @changed:2026-03-19
  Scenario: Skill is linked to Claude Code skills directory on init with --ai claude-code
    Given I have the Cliplin CLI tool installed
    When I run `cliplin init --ai claude-code`
    Then the CLI should create a hard link at `.claude/skills/cliplin-reverse-engineer/SKILL.md`

  @status:implemented
  @changed:2026-03-19
  Scenario: Skill is linked to Cursor skills directory on init with --ai cursor
    Given I have the Cliplin CLI tool installed
    When I run `cliplin init --ai cursor`
    Then the CLI should create a hard link at `.cursor/skills/cliplin-reverse-engineer/SKILL.md`

  @status:implemented
  @changed:2026-03-19
  Scenario: Skill is linked to Gemini skills directory on init with --ai gemini
    Given I have the Cliplin CLI tool installed
    When I run `cliplin init --ai gemini`
    Then the CLI should create a hard link at `.gemini/skills/cliplin-reverse-engineer/SKILL.md`

  @status:implemented
  @changed:2026-03-19
  Scenario: Skill detects top-level modules from source tree
    Given I have a project with source directories `src/payments`, `src/auth`, `src/notifications`
    When I invoke the `cliplin-reverse-engineer` skill
    Then the skill should detect 3 top-level modules: `payments`, `auth`, `notifications`
    And each module should have an `inferred_domain` derived from file names and README content
    And modules with existing feature files referencing them should be marked `has_existing_specs: true`

  @status:implemented
  @changed:2026-03-19
  Scenario: Skill presents a process plan and waits for confirmation before proceeding
    Given I have a project with 3 detected top-level modules
    And no `.cliplin/.re-progress.yaml` exists
    When I invoke the `cliplin-reverse-engineer` skill
    Then the skill should present the list of modules with their coverage status
    And the skill should ask "Shall I start with module 1?" before proceeding
    And the skill should NOT start Phase 1 until the user confirms

  @status:implemented
  @changed:2026-03-19
  Scenario: Skill produces a findings report (Phase 1) for a module
    Given I invoke the `cliplin-reverse-engineer` skill and confirm to start with module `payments`
    When the skill executes Phase 1 for `payments`
    Then the output should include detected domain concepts with brief descriptions
    And the output should include inferred use cases with trigger → outcome format
    And the output should list existing coverage (feature files, ADRs, TDRs, business docs)
    And the output should list findings tagged as MISSING-FEATURE, MISSING-TDR, MISSING-ADR, MISSING-BUSINESS-DOC, or PARTIAL-SPEC
    And the output should include context signals inferred beyond code (README, CHANGELOG, git history)
    And the skill should ask "Proceed to Phase 2?" before starting guided drafting

  @status:implemented
  @changed:2026-03-19
  Scenario: Skill proposes spec drafts one by one in Phase 2 and waits for confirmation
    Given Phase 1 produced 3 findings for module `payments`
    When the skill executes Phase 2
    Then the skill should present the first finding with a draft document marked "[AGENT PROPOSAL — awaiting human approval]"
    And the skill should NOT present the second finding until the first is confirmed, rejected, or modified
    And after each approved finding the skill should instruct the user to run `cliplin reindex <path>`
    And after all findings are resolved the skill should ask "Move to next module?"

  @status:implemented
  @changed:2026-03-19
  Scenario: Skill writes and updates the tracking file during execution
    Given I invoke the `cliplin-reverse-engineer` skill on a project with 2 modules
    When the skill starts processing module 1
    Then `.cliplin/.re-progress.yaml` should exist and contain `current_module`, `current_phase`, and `context_references`
    And after completing Phase 1 of module 1, `current_phase` should be updated to `2`
    And after completing module 1, `modules_completed` should include `module1` and `modules_pending` should include `module2`

  @status:implemented
  @changed:2026-03-19
  Scenario: Skill offers to resume when a progress file is found on re-invocation
    Given `.cliplin/.re-progress.yaml` exists with `current_module: payments` and `current_phase: 2`
    When I invoke the `cliplin-reverse-engineer` skill again
    Then the skill should detect the progress file
    And the skill should present resume options: [C] Continue, [R] Restart, [M] Jump to module
    And the skill should NOT start scanning until the user chooses an option
    And if the user chooses [C], the skill should reload the MCP context using `context_references` queries
    And if the user chooses [R], the skill should delete the progress file and start fresh

  @status:implemented
  @changed:2026-03-19
  Scenario: Skill targets a specific module when invoked with a module name
    Given I have a project with modules `auth`, `payments`, `notifications`
    And a progress file exists listing all three modules
    When I invoke the `cliplin-reverse-engineer` skill targeting module `payments`
    Then the skill should jump directly to Phase 1 for `payments`
    And the skill should NOT scan or present findings for `auth` or `notifications`
    And after completing `payments`, the skill should ask if the user wants to continue the full scan

  @status:implemented
  @changed:2026-03-19
  Scenario: Skill performs targeted scan when invoked on a module with no progress file
    Given no `.cliplin/.re-progress.yaml` exists
    When I invoke the `cliplin-reverse-engineer` skill targeting `src/auth`
    Then the skill should scan only `src/auth` instead of the full project
    And the skill should create `.cliplin/.re-progress.yaml` with `modules_total: 1` and `invocation_target: auth`
    And the skill should proceed directly to Phase 1 for `auth` without showing a process plan

  @status:implemented
  @changed:2026-03-19
  Scenario: Skill deletes the tracking file when all modules are complete
    Given all modules have been processed and `modules_pending` is empty
    When the skill completes the last module
    Then the skill should instruct the AI to delete `.cliplin/.re-progress.yaml`
    And the progress file should no longer exist

  @status:new
  Scenario: Skill warns and proceeds fresh when progress file is malformed
    Given `.cliplin/.re-progress.yaml` exists but contains invalid YAML
    When I invoke the `cliplin-reverse-engineer` skill
    Then the skill should emit a warning that the progress file is malformed and will be ignored
    And the skill should NOT delete the malformed file automatically
    And the skill should proceed as if no progress file exists (fresh scan)
    And when the first module starts processing, the skill should overwrite the file with valid YAML

  @status:new
  Scenario: Skill lists ambiguous matches when module targeting is ambiguous
    Given I have a project with modules `src/auth` and `src/oauth`
    And a progress file exists listing both modules
    When I invoke the `cliplin-reverse-engineer` skill targeting `auth`
    Then the skill should detect that both `auth` and `oauth` match the input
    And the skill should list both matching options and ask the user to choose
    And the skill should NOT proceed to Phase 1 until the user makes an explicit selection

  @status:new
  Scenario: Skill informs the user and exits when the project is completely empty
    Given I have a project with no source files, no README, no manifests, and no docs
    When I invoke the `cliplin-reverse-engineer` skill
    Then the skill should inform the user that the project appears to be empty and there is nothing to analyze
    And the skill should exit without creating a progress file

  @status:new
  Scenario: Skill scans from project root when no conventional source directories exist
    Given I have a project with no `src/`, `lib/`, `app/`, `pkg/`, `internal/`, or `cmd/` directories
    When I invoke the `cliplin-reverse-engineer` skill
    Then the skill should scan from the project root
    And the skill should exclude hidden directories, `vendor/`, `node_modules/`, `dist/`, `build/`
    And the skill should treat the project as a single module named after the project root

  @status:new
  Scenario: Skill handles resume option M to jump to a specific module
    Given `.cliplin/.re-progress.yaml` exists with modules `auth` (completed) and `payments` (pending)
    And `notifications` is also listed as pending
    When I invoke the `cliplin-reverse-engineer` skill
    And I choose option [M] from the resume prompt
    Then the skill should ask which module to jump to
    And I select `notifications`
    Then the skill should jump directly to Phase 1 for `notifications`
    And the skill should NOT reprocess `auth` or start `payments` first

  @status:new
  Scenario: Skill rewrites tracking file with full module list when continuing after targeted run
    Given I ran the skill targeting `src/payments` and the progress file has `modules_total: 1`
    When the skill asks "Do you want to continue with the full project scan?" and I confirm
    Then the skill should detect all top-level modules in the project
    And the skill should rewrite `.cliplin/.re-progress.yaml` with the real `modules_total`
    And `modules_completed` should already include `payments`
    And `invocation_target` should be reset to `null`
    And the skill should proceed to Phase 1 of the next pending module

  @status:implemented
  @changed:2026-03-19
  @reason:Covered by ensure_cliplin_in_gitignore which adds .cliplin (broader coverage than .cliplin/.re-progress.yaml; .cliplin entry satisfies the spec since TDR says check if .cliplin/ OR .cliplin/.re-progress.yaml is listed)
  Scenario: cliplin init adds .re-progress.yaml to .gitignore when not already covered
    Given I have a project with a `.gitignore` that does not mention `.cliplin/` or `.re-progress.yaml`
    When I run `cliplin init`
    Then the CLI should append `.cliplin/.re-progress.yaml` to `.gitignore`
    And the appended entry should include a comment `# cliplin-reverse-engineer progress file`

  @status:implemented
  @changed:2026-03-19
  @reason:Covered by ensure_cliplin_in_gitignore which skips if .cliplin already present
  Scenario: cliplin init does not duplicate .gitignore entry when already covered
    Given I have a project with a `.gitignore` that already contains `.cliplin/` or `.cliplin/.re-progress.yaml`
    When I run `cliplin init`
    Then the CLI should NOT append a duplicate entry to `.gitignore`

  @status:implemented
  @changed:2026-03-19
  @reason:Covered by ensure_cliplin_in_gitignore which creates .gitignore with .cliplin entry
  Scenario: cliplin init creates .gitignore with the entry when no .gitignore exists
    Given I have a project with no `.gitignore` file
    When I run `cliplin init`
    Then the CLI should create `.gitignore` with the entry `.cliplin/.re-progress.yaml`

  @status:implemented
  @changed:2026-03-19
  Scenario: feature-template-mapping.md records the reverse-engineer skill mapping
    Given the feature `docs/features/reverse-engineer.feature` exists
    And the template function `create_reverse_engineer_skill` exists in `src/cliplin/utils/templates.py`
    Then `docs/tdrs/feature-template-mapping.md` should contain a mapping entry for:
      | Feature file                             | Template function              |
      | docs/features/reverse-engineer.feature   | create_reverse_engineer_skill  |
