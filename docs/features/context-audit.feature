@constraints
# governed_by:
#   - docs/tdrs/context-audit-skill.md
#   - docs/tdrs/knowledge-packages.md
#   - docs/tdrs/ai-host-integration.md
#   - docs/tdrs/ai-host-integration-handler-pattern.md
#   - docs/tdrs/claude-desktop-integration.md
#   - docs/tdrs/feature-template-mapping.md
#   - docs/tdrs/system-modules.md
#   - docs/tdrs/cliplin-cli-stack.md
# conflicts: []
# gaps:
#   - "No spec for how the skill behaves when docs/features/ does not exist at all (project not yet initialized)"
#   - "No scenario tests scenario-level @constraints block aggregation specifically (TDR says include them but no dedicated test)"
#   - "No scenario tests what happens when a @constraints block is malformed (unparseable YAML comments) — expected behavior is skip-and-continue or emit a warning field"
#   - "No scenario tests that framework files (.cliplin/knowledge/cliplin-framework/**) are excluded from dead_documentation"
#   - "No scenario tests that init with --ai gemini completes without error when no skill linking is performed"
# escalation_triggers:
#   - "If the call site for link_knowledge_skills(framework_package) is ambiguous during implementation (create_framework_knowledge_package cannot know the AI host), stop and ask: confirm the call goes in each integration handler's apply() method after create_framework_knowledge_package"
#   - "If the context_score formula produces a negative number (more deductions than 100 points available), stop and ask: confirm the minimum is clamped at 0"
#   - "If hard-linking the skill from the framework package fails at init time (OSError, cross-filesystem), stop and ask: should init warn and continue, or fail with an error?"
#   - "If the implementer finds that create_framework_knowledge_package is called before the integration apply() in the init flow (wrong order), stop and ask: confirm init order and adjust call site accordingly"
Feature: cliplin-context-audit Built-in Skill
  As a developer using Cliplin
  I want a built-in audit skill that analyzes my project's context health
  So that I can identify gaps, conflicts, drift, and dead documentation without leaving my AI assistant

  Background:
    Given I have initialized a Cliplin project
    And the project has a `.cliplin/knowledge/cliplin-framework/` built-in package

  @status:implemented
  @changed:2026-03-18
  Scenario: Skill file is created inside the framework package on cliplin init
    Given I have the Cliplin CLI tool installed
    And I am in an empty directory
    When I run `cliplin init`
    Then the CLI should create the skill at `.cliplin/knowledge/cliplin-framework/skills/cliplin-context-audit/SKILL.md`
    And the SKILL.md file should contain the full JSON output schema
    And the SKILL.md file should explain the context_score computation formula
    And the SKILL.md file should instruct the AI to output only valid JSON to stdout

  @status:implemented
  @changed:2026-03-18
  Scenario: Skill is linked to Claude Code skills directory on init with --ai claude-code
    Given I have the Cliplin CLI tool installed
    And I am in an empty directory
    When I run `cliplin init --ai claude-code`
    Then the CLI should create the skill at `.cliplin/knowledge/cliplin-framework/skills/cliplin-context-audit/SKILL.md`
    And the CLI should create a hard link at `.claude/skills/cliplin-context-audit/SKILL.md` pointing to the skill source
    And the `.claude/skills/cliplin-context-audit/` directory should exist

  @status:implemented
  @changed:2026-03-18
  Scenario: Skill is linked to Cursor skills directory on init with --ai cursor
    Given I have the Cliplin CLI tool installed
    And I am in an empty directory
    When I run `cliplin init --ai cursor`
    Then the CLI should create the skill at `.cliplin/knowledge/cliplin-framework/skills/cliplin-context-audit/SKILL.md`
    And the CLI should create a hard link at `.cursor/skills/cliplin-context-audit/SKILL.md` pointing to the skill source
    And the `.cursor/skills/cliplin-context-audit/` directory should exist

  @status:implemented
  @changed:2026-03-18
  Scenario: Skill link is refreshed when cliplin init is run again
    Given I have initialized a Cliplin project with `cliplin init --ai claude-code`
    And the skill link exists at `.claude/skills/cliplin-context-audit/SKILL.md`
    When I run `cliplin init --ai claude-code` again and confirm to continue
    Then the CLI should remove the existing skill link
    And the CLI should recreate the hard link at `.claude/skills/cliplin-context-audit/SKILL.md`
    And the skill content should reflect the latest SKILL.md from the framework package

  @status:implemented
  @changed:2026-03-18
  Scenario: Skill is not linked when AI host does not support skills
    Given I have the Cliplin CLI tool installed
    And I am in an empty directory
    When I run `cliplin init --ai gemini`
    Then the CLI should create the skill at `.cliplin/knowledge/cliplin-framework/skills/cliplin-context-audit/SKILL.md`
    And no `.gemini/skills/` directory should be created
    And no skill link should be created for the gemini host
    And the CLI should complete successfully without error

  @status:implemented
  @changed:2026-03-18
  Scenario: Audit skill produces JSON output for a well-specified project
    Given I have a Cliplin project with feature files in `docs/features/`
    And all feature files have `@constraints` blocks with non-empty `governed_by` lists
    And all referenced `governed_by` files exist on disk
    And there are no gaps or conflicts recorded in any `@constraints` block
    When I invoke the `cliplin-context-audit` skill in my AI assistant
    Then the AI should output a single valid JSON object to stdout
    And the JSON should contain all required fields:
      | Field                     | Expected value                             |
      | generated_at              | ISO 8601 UTC datetime string               |
      | project_root              | Absolute path to project root              |
      | context_score             | Integer 0-100                              |
      | features_total            | Count of .feature files in docs/features/  |
      | features_with_constraints | Equal to features_total                    |
      | gaps                      | Empty array                                |
      | conflicts                 | Empty array                                |
      | context_drift             | Empty array                                |
      | dead_documentation        | Empty array                                |
    And `context_score` should equal 100 when there are no issues

  @status:implemented
  @changed:2026-03-18
  Scenario: Audit skill reports missing @constraints blocks
    Given I have a Cliplin project with 4 feature files in `docs/features/`
    And 2 of those feature files have no `@constraints` block
    When I invoke the `cliplin-context-audit` skill
    Then the JSON output should have `features_total` equal to 4
    And the JSON output should have `features_with_constraints` equal to 2
    And `context_score` should be less than 100

  @status:implemented
  @changed:2026-03-18
  Scenario: Audit skill collects gaps from @constraints blocks and deduplicates
    Given I have a Cliplin project with feature files
    And one feature file has a `@constraints` block with:
      """
      # gaps:
      #   - "No spec for timeout behavior"
      #   - "No spec for retry logic"
      """
    And another feature file has a `@constraints` block with:
      """
      # gaps:
      #   - "No spec for timeout behavior"
      """
    When I invoke the `cliplin-context-audit` skill
    Then the JSON `gaps` array should contain exactly 2 unique entries after deduplication
    And `context_score` should be reduced by 2 per unique gap entry

  @status:implemented
  @changed:2026-03-18
  Scenario: Audit skill collects conflicts from @constraints blocks
    Given I have a Cliplin project with feature files
    And one feature file has a `@constraints` block with:
      """
      # conflicts:
      #   - "TDR-A and TDR-B disagree on retry policy"
      """
    When I invoke the `cliplin-context-audit` skill
    Then the JSON `conflicts` array should contain 1 entry
    And `context_score` should be reduced by 5 for that conflict entry

  @status:implemented
  @changed:2026-03-18
  Scenario: Audit skill detects context drift when a governed_by file does not exist
    Given I have a Cliplin project with a feature file
    And the feature file's `@constraints` block lists `docs/tdrs/deleted-tdr.md` in `governed_by`
    And the file `docs/tdrs/deleted-tdr.md` does not exist on disk
    When I invoke the `cliplin-context-audit` skill
    Then the JSON `context_drift` array should contain 1 entry
    And the entry should identify both the feature file and the missing governed_by path `docs/tdrs/deleted-tdr.md`
    And `context_score` should be reduced by 3 for that drift entry

  @status:implemented
  @changed:2026-03-18
  Scenario: Audit skill identifies orphaned documentation as dead_documentation
    Given I have a Cliplin project with TDR files in `docs/tdrs/`
    And `docs/tdrs/orphaned-tdr.md` is not referenced in any `governed_by` list in any feature file
    And `docs/tdrs/active-tdr.md` is referenced in at least one `governed_by` list
    When I invoke the `cliplin-context-audit` skill
    Then the JSON `dead_documentation` array should contain `docs/tdrs/orphaned-tdr.md`
    And `docs/tdrs/active-tdr.md` should NOT appear in `dead_documentation`

  @status:implemented
  @changed:2026-03-18
  Scenario: Audit skill outputs empty JSON structure when no feature files exist
    Given I have initialized a Cliplin project
    And the `docs/features/` directory exists but contains no `.feature` files
    When I invoke the `cliplin-context-audit` skill
    Then the AI should output a valid JSON object with:
      | Field                     | Value |
      | features_total            | 0     |
      | features_with_constraints | 0     |
      | context_score             | 100   |
      | gaps                      | []    |
      | conflicts                 | []    |
      | context_drift             | []    |
      | dead_documentation        | []    |
    And the output should be valid JSON, not an error message

  @status:implemented
  @changed:2026-03-18
  Scenario: feature-template-mapping.md records the context-audit skill mapping
    Given the feature `docs/features/context-audit.feature` exists
    And the template function `create_context_audit_skill` exists in `src/cliplin/utils/templates.py`
    Then `docs/tdrs/feature-template-mapping.md` should contain a mapping entry for:
      | Feature file                        | Template function          |
      | docs/features/context-audit.feature | create_context_audit_skill |
