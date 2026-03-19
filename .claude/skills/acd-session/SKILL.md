# Skill: acd-session

Run a single ACD-compliant implementation session: atomic, small-batch, traceable to an approved Agent Delivery Contract.

## When to use this skill

Use this skill when:
- The ADC is complete (`.feature` file with approved `@constraints` block exists).
- The CI pipeline is green.
- The human has confirmed which scenarios to implement in this session.

Do NOT use this skill when:
- The ADC is incomplete — run `acd-spec-cycle` first.
- The pipeline is red — run pipeline repair first (`acd-pipeline-gates.md`).
- The session would span more than 3 scenarios or more than one feature.

## Instructions

### Step 0: Pre-session checklist

Before writing any code, detect the session mode and verify the checklist.

**Detect session mode** by reading the scenarios in scope:
- If all in-scope scenarios are `@status:new` or `@status:pending` → **Authorship session**
- If any in-scope scenario is `@status:modified` → **Evolution session**

Report mode and checklist to the human:

```
Session mode: Authorship / Evolution
[ ] Pipeline status: green / red (if red → STOP, run pipeline repair)
[ ] ADC complete: .feature file exists with @constraints block
[ ] governed_by populated: [list the docs]
[ ] Scenarios in scope: [list max 3, with their current @status tag]
[ ] Context loaded from Cliplin MCP: TDRs, ADRs, related features
```

Do not proceed if any item is unchecked. Report the blocker to the human.

### Step 1: Load implementation context

Query the Cliplin MCP for the technical constraints governing this session:

```
1. Query 'technical-decision-records' → TDRs listed in governed_by
2. Query 'business-and-architecture' → ADRs listed in governed_by
3. Query 'features' → related features that may be affected
```

Re-read the full `@constraints` block before writing any code. Specifically note the `escalation_triggers` list — these are conditions that, if encountered during implementation, require stopping immediately and asking the human.

### Step 2: Implement (TDD, domain-first)

For each scenario in scope (non-deprecated), apply the workflow that matches its status:

**For `@status:new` or `@status:pending` (authorship workflow):**

1. **Write the failing test first** (unit test or BDD step definition) that maps to the scenario.
2. **Implement domain logic** to make the test pass.
3. **Do not touch infrastructure adapters** unless the scenario explicitly requires it.
4. **Verify**: run the test suite locally after each scenario.

**For `@status:modified` (evolution workflow):**

1. **Read the existing implementation** for the scenario before writing anything. Understand what the current behavior is and how it differs from the modified scenario.
2. **Update the existing test first** to reflect the new expected behavior — the test should fail against the old implementation.
3. **Update the domain logic** to make the updated test pass.
4. **Run the full test suite** — not just the updated test. Any regression in a `@status:implemented` scenario outside the delta is a blocking issue: STOP and report to the human before continuing.
5. **Do not touch scenarios outside the delta** even if refactoring them would be cleaner.

Constraints during implementation (both workflows):
- No imports from outside the domain layer in domain files (follow hexagonal architecture if applicable).
- No access to real external systems (databases, APIs).
- If a TDR rule blocks the implementation, STOP and report to the human before finding a workaround.
- If an `escalation_trigger` condition is encountered, STOP immediately — do not implement a default or assumption. Report the trigger, describe the situation, and present options to the human. Resume only after an explicit decision.
- If a new gap or conflict is detected, add it to the `@constraints` block and inform the human.

### Step 3: Update the feature file

For each implemented scenario, update its tags:

```gherkin
@status:implemented
@changed:YYYY-MM-DD
Scenario: <scenario name>
  Given ...
```

- Replace `@status:new`, `@status:pending`, or `@status:modified` with `@status:implemented`.
- Add `@changed` with today's date.
- Add `@reason` only if the implementation required a decision not obvious from the scenario.

### Step 4: Verify before committing

Run locally before committing:

- [ ] All unit tests pass
- [ ] All BDD tests for in-scope scenarios pass
- [ ] No other tests regressed (mandatory for evolution sessions — run the full suite)
- [ ] The `.feature` file shows `@status:implemented` for all in-scope scenarios
- [ ] **Evolution only**: no `@status:implemented` scenario outside the delta changed behavior

If any check fails, fix it before committing. Do not commit red tests.

### Step 4.5: Run acd-commit-validator (blocking gate)

**This step is mandatory and blocks the commit. Do not proceed to Step 5 unless the validator returns `ACD-VALIDATION: PASS`.**

Stage all changes, then invoke the `acd-commit-validator` skill:

```
Run acd-commit-validator on the current staged changes.
```

#### If `ACD-VALIDATION: PASS`

Proceed to Step 5.

#### If `ACD-VALIDATION: FAIL` — feedback loop

Do NOT commit. Enter the fix-and-retry cycle:

1. **Read the violation list** produced by the validator report (AC-*, UD-*, TR-*, EX-* checks).
2. **For each FAIL violation**, apply the corresponding fix:
   - `[AC-1]` — stage the missing `.feature` file or add the scenario that covers the changed code.
   - `[AC-2]` — add or complete the `@constraints` block in the feature file (`governed_by` must be populated).
   - `[AC-3]` — create the missing document referenced in `governed_by`, or correct the path.
   - `[AC-4]` — update the scenario tag to `@status:implemented @changed:YYYY-MM-DD`.
   - `[UD-1]` — stage the missing test files alongside the production changes.
   - `[UD-2]` — the commit message will be set in Step 5; skip this check in the feedback loop if the commit has not been made yet.
   - `[TR-1]` — stage the corresponding `.feature` update or add `[skip-TR-1]` with justification if this is truly infra-only.
   - `[EX-*]` — read the expert's `Fixes:` block and apply each fix. If the fix requires a spec change, update the relevant TDR/ADR and reindex before retrying.
3. **Re-stage all modified files** after applying the fixes.
4. **Re-run `acd-commit-validator`** (repeat from the top of this step).
5. **Repeat until `ACD-VALIDATION: PASS`** is received, or until a violation cannot be resolved autonomously.

#### Escalation during the feedback loop

If after one full fix iteration a FAIL violation persists and cannot be resolved without a spec change or human decision:

1. STOP the feedback loop.
2. Report to the human:
   ```
   acd-commit-validator FAIL — feedback loop blocked.
   Unresolved violation: [<check-id>] <description>
   Reason it cannot be auto-fixed: <explanation>
   Options:
     A) <option 1>
     B) <option 2>
   ```
3. Wait for an explicit human decision before resuming.

WARNs (`UD-3`, `TR-2`) do not block the commit and do not require fixes — report them to the human in Step 6.

### Step 5: Commit and open PR

Commit all changes atomically using this format:

```
<type>(<scope>): <short description>

ACD-session: <scenario or feature name>
Artifacts: <comma-separated list of ADC files changed>
Scenarios: @status:implemented — "<scenario 1>", "<scenario 2>"
```

Then open a PR with:
- **Title**: same as the commit subject.
- **Body**:
  - Which scenarios this PR implements.
  - Which ADC artifacts are included.
  - Any gaps or conflicts resolved during the session.
  - Any new gaps added to the `@constraints` block.

**Never merge the PR.** Leave it for human review or an authorized validation agent.

### Step 6: Post-session report

After opening the PR, report to the human:

```
Session complete.
PR: <PR URL>
Scenarios implemented: <list>
Artifacts updated: <list>
Remaining scenarios: <list of scenarios not yet implemented in this feature>
Pipeline status: green / awaiting CI
Next session: ready / blocked by [reason]
```

## Context window management

If you detect you are approaching the context limit mid-session:

1. Commit what is implemented so far with `[WIP-ACD]` prefix in the commit message.
2. Do NOT open a PR for a WIP commit.
3. Report to the human: "Context limit approaching. Partial commit made. Start a new session to continue."
4. The new session starts from Step 0 with a fresh context load.

## Output checklist

- [ ] Session mode detected and reported: Authorship / Evolution (Step 0)
- [ ] Pre-session checklist verified (Step 0)
- [ ] Context loaded from Cliplin MCP (Step 1)
- [ ] All in-scope scenarios implemented with correct workflow per status tag (Step 2)
- [ ] Evolution: full test suite run, no regressions in implemented scenarios (Step 2)
- [ ] `.feature` file updated with `@status:implemented` and `@changed` (Step 3)
- [ ] All tests pass locally (Step 4)
- [ ] `acd-commit-validator` returned `ACD-VALIDATION: PASS` (Step 4.5) ← **blocking gate**
- [ ] Feedback loop completed with zero FAIL violations before committing (Step 4.5)
- [ ] Atomic commit with ACD format message (Step 5)
- [ ] PR opened — NOT merged (Step 5)
- [ ] Post-session report delivered to human (Step 6)

## References

- `cliplin-acd/tdrs/acd-agent-delivery-contract.md`
- `cliplin-acd/tdrs/acd-session-workflow.md`
- `cliplin-acd/tdrs/acd-pipeline-gates.md`
- `cliplin-acd/skills/acd-spec-cycle/SKILL.md`
