# Skill: acd-spec-cycle

Run the ACD specification cycle to produce or evolve an Agent Delivery Contract (ADC) before any implementation begins. Operates in two modes: **authorship** (new feature) and **evolution** (existing feature with approved spec).

## When to use this skill

Use this skill when:
- The human has a new feature request and wants to produce ACD-compliant specs before implementation.
- An existing `.feature` file needs a new scenario, a behavior change, or a deprecation.
- The `@constraints` block is missing or incomplete.
- The human suspects conflicts between governing docs and wants the agent to surface them.

Do NOT use this skill when:
- The `.feature` file already has an approved `@constraints` block and the human only wants to start implementing — go directly to `acd-session`.

---

## Mode detection

Before starting, determine which mode applies by reading the `.feature` file (if it exists):

| Condition | Mode |
|---|---|
| No `.feature` file exists | **Authorship** |
| `.feature` file exists but `@constraints` is missing or `governed_by` is empty | **Authorship** |
| `.feature` file exists with approved `@constraints` and `governed_by` populated | **Evolution** |

Announce the detected mode to the human before proceeding:
> "I detected this is an **[Authorship / Evolution]** cycle for `<feature-file>`. [brief reason]"

---

## Context loading (mandatory, both modes)

Before any assessment or modification, load all relevant context from the Cliplin MCP:

```
1. Query 'business-and-architecture' → ADRs related to the feature domain
2. Query 'technical-decision-records' → TDRs that constrain the feature
3. Query 'features' → related or dependent features
4. Query 'uisi' → if the feature involves UI/UX
```

Context must be loaded before evaluating intent clarity, gaps, or drafting anything. Do not skip this step even if the request seems straightforward — the loaded context may resolve apparent ambiguities without requiring an interview.

---

## Authorship mode

Used when creating a feature spec from scratch.

### Step 0: Intent clarity assessment

After loading context, evaluate whether the human's request is concrete enough to proceed.

**The test**: can the agent formulate at least one Given/When/Then scenario that captures the request without making assumptions the human has not confirmed? If yes → intent is clear, proceed to Step 0.5. If no → intent is vague, go to **Step 0i: Interview cycle**.

Consider the request clear if the loaded context resolves the ambiguity. Examples:
- Request: "add authentication" — vague in isolation, but if a TDR already defines the auth mechanism (e.g. OAuth + JWT), the scope becomes clear → proceed
- Request: "improve the user experience" — context cannot resolve this; no observable behavior can be inferred → interview required

If intent is clear, announce:
> "Intent is clear. Proceeding to context gap assessment."

If intent is vague, announce:
> "The request needs more definition before I can draft scenarios. Starting an interview — I'll ask a few focused questions."

### Step 0i: Interview cycle (only if intent is vague)

Three phases. Keep it short — the goal is the minimum information needed to write a confirmed intent statement, not a full requirements session.

**Phase 1 — Framing**

Restate what the agent understood from the request and ask one open question:

```
I understood you want to: <agent's interpretation of the request>
Based on the loaded context, I can see: <relevant existing decisions, related features, constraints>

To write a concrete spec, I need to understand:
  What is the specific observable outcome when this feature works correctly?
  (Describe what a user would see, receive, or be able to do that they cannot do today)
```

Wait for the human's answer before proceeding.

**Phase 2 — Deep-dive**

Based on the human's answer and the loaded context, identify the gaps that remain. Ask a maximum of 4 focused questions derived from what the context does not resolve. Do not ask about things the context already answers.

Derive questions from the feature's actual needs. Examples of high-signal question areas:
- Who is the actor and what triggers the behavior?
- What are the failure modes and what should the system do when they occur?
- Are there boundaries or limits (volume, time, size, roles) that define the edges of this behavior?
- What is explicitly out of scope for this feature?

Format:
```
A few questions to complete the picture:
1. <question>
2. <question>
3. <question (optional)>
4. <question (optional)>
```

Wait for the human's answers before proceeding.

**Phase 3 — Synthesis and confirmation**

Synthesize the conversation into an intent statement and a first tentative scenario:

```
Based on our conversation, here is the intent:

Feature: <Feature Name>
  <2-3 sentence description of what this feature does, why, and for whom>

First scenario (tentative):
  Scenario: <scenario name>
    Given <precondition>
    When <action>
    Then <observable outcome>

Does this capture what you need? Confirm or correct before I proceed.
```

Wait for explicit human confirmation or correction. Iterate within this phase if the human adjusts the intent. Do not proceed to Step 0.5 until the intent statement is confirmed.

The confirmed `Feature: <description>` block is human-owned from this point forward. The agent does not rewrite it in subsequent steps.

### Step 0.5: Context gap assessment

With a clear intent (either from the start or from the interview), assess whether foundational technical decisions exist to govern implementation.

These are gaps at the project level — not in the feature itself — that would leave `governed_by` empty or incomplete if not resolved first.

Reason from the confirmed intent:

1. Ask: *"What technical decisions must already exist for an agent to implement this feature correctly and consistently?"*
2. For each required decision, check whether a TDR or ADR covering it exists in the context store.
3. If a required decision is undocumented, flag it as a `[CONTEXT-GAP]`.

The set of gaps is derived from the feature — not from a predefined taxonomy. A REST API feature may surface stack and routing decisions. A UI feature may surface design system, state management, and rendering decisions. A data pipeline feature may surface processing guarantees and schema evolution decisions. Let the feature drive what questions arise.

If any `[CONTEXT-GAP]` is found, do NOT proceed to Step 1. Instead, go to **Step 0.6**.

If no context gaps are found, proceed to Step 1.

### Step 0.6: Resolve foundational context gaps (only if gaps found in Step 0.5)

For each `[CONTEXT-GAP]` detected, derive the questions from what the feature actually needs — not from a template.

**Format for each gap:**

```
[CONTEXT-GAP] <short label derived from the feature need>: <what decision is missing and why it blocks this feature>

To implement this feature, the following needs to be decided and documented:
  - <question derived from the feature requirement>
  - ...

Suggested default: <recommendation based on the feature domain, project signals, and existing context>
```

**After the human answers each gap:**

1. The agent drafts the corresponding ADR or TDR (marked `[AGENT PROPOSAL — awaiting human approval]`).
2. The human approves or modifies.
3. The agent writes the file to the appropriate path (`docs/adrs/` or `docs/tdrs/`).
4. Ask the human: *"Do you want to reindex this file now with `cliplin reindex <path>`?"*
5. Once reindexed, reload context from the MCP before continuing.

Only after all `[CONTEXT-GAP]` items are resolved and their documents exist in the repo may the cycle continue to Step 1.

### Step 1: Human drafts (or requests a draft)

If the interview cycle ran, the confirmed intent statement is already the `Feature:` block. The agent proceeds to draft scenarios only — it does not re-propose the feature description.

If no interview ran, the human either:
- **Provides a draft** of the scenarios or intent. The agent receives it as input.
- **Requests a draft**: The agent proposes scenarios based on the confirmed intent. Mark every agent-proposed element clearly: `[AGENT PROPOSAL — awaiting human approval]`.

**The `Feature: <description>` block is human-owned.** The agent never rewrites or replaces it, only proposes scenario content beneath it.

Output of Step 1: a draft `.feature` file (or updated scenarios) with clear ownership markers.

### Step 2: Agent critiques

The agent systematically reviews the draft against the loaded project context and produces a critique report:

**Context gaps** (governing docs exist but don't cover this feature's specific behavior):
- Behavior assumed by the feature not addressed by any TDR or ADR
- Missing rules for domain-specific validations or error states
- Feature relies on infrastructure decisions not yet documented

**Behavioral gaps** (assumed behavior not specified in the feature itself):
- Edge cases not covered by any scenario
- Error states not described
- Missing actors or preconditions

**Conflicts** (contradictions between the draft and governing docs):
- Scenarios that contradict an existing TDR rule
- Business logic that conflicts with an ADR decision
- Inconsistencies between this feature and related features in the context store

**Ambiguities** (unclear intent):
- Steps that could be interpreted in more than one way
- Missing Given/When/Then precision

Format the critique as a numbered list:
`[CONTEXT-GAP|GAP|CONFLICT|AMBIGUITY] <description> → Suggested resolution: <suggestion>`

Do NOT modify the `.feature` file in this step. Only produce the critique report.

### Step 3: Human decides

Present the critique report to the human and wait for explicit decisions on each item:
- **Accept**: incorporate the suggested resolution.
- **Reject**: keep the original; document the human's reasoning as a comment.
- **Modify**: the human provides an alternative resolution.
- **Create doc**: for `[CONTEXT-GAP]` items, the agent drafts a new TDR or ADR and the human approves it before continuing.

Do not proceed to Step 4 without explicit human decisions on all `[CONTEXT-GAP]`, `[GAP]`, and `[CONFLICT]` items. `[AMBIGUITY]` items may be deferred if the human explicitly says so.

### Step 4: Agent refines

Apply all accepted and modified resolutions to the `.feature` file. Then write the `@constraints` block:

```gherkin
@constraints
# governed_by:
#   - docs/tdrs/<tdr-file>.md
#   - docs/adrs/<adr-file>.md
# conflicts:
#   - "<any unresolved conflict the human chose to keep, with justification>"
# gaps:
#   - "<any gap the human chose to accept without a new doc>"
# escalation_triggers:
#   - "<condition that, if encountered during implementation, requires stopping and asking the human>"
Feature: <Feature Name>
  <description>
  ...
```

Rules for the `@constraints` block:
- `governed_by` must list every TDR, ADR, and business doc that actively constrains this feature — including any docs created in Steps 0.6 or 3.
- `conflicts: []` if all conflicts were resolved.
- `gaps: []` if all gaps were documented or resolved.
- `escalation_triggers: []` if no conditions require mid-implementation human decisions. Otherwise list each trigger as a specific condition the agent may encounter (not a category — a concrete situation). These are a safety net for cases not caught as gaps during spec; if a trigger fires during `acd-session`, the agent stops and waits for human input.
- If a scenario has constraints different from the feature-level ones, add a scenario-level `@constraints` block immediately before that `Scenario:` line.

### Authorship output checklist

- [ ] Context loaded from Cliplin MCP (pre-step)
- [ ] Intent clarity assessed after context load (Step 0)
- [ ] Interview cycle completed and intent statement confirmed (Step 0i, if needed)
- [ ] Foundational context gaps assessed (Step 0.5)
- [ ] All `[CONTEXT-GAP]` items resolved — ADRs/TDRs created and approved (Step 0.6, if needed)
- [ ] Draft `.feature` file produced with human-owned `Feature:` block (Step 1)
- [ ] Critique report delivered with all gap/conflict types identified (Step 2)
- [ ] Human decisions received on all critical items (Step 3)
- [ ] `.feature` file refined with all accepted resolutions (Step 4)
- [ ] `@constraints` block written with `governed_by` and `escalation_triggers` populated
- [ ] Human confirmed readiness for implementation

---

## Evolution mode

Used when an existing `.feature` file with an approved `@constraints` block needs to grow or change. The existing spec is the **baseline** — only the delta is put through the cycle.

### Evo-Step 0: Load context and read the baseline

1. Load all relevant context from the Cliplin MCP (same queries as the context loading pre-step).
2. Read the existing `.feature` file in full, including the `@constraints` block.
3. Identify the current `governed_by` list — these docs are already in scope.
4. Summarize the baseline to the human:

```
Baseline: <feature-file>
Governed by: <list of docs from governed_by>
Active scenarios: <count> implemented, <count> pending, <count> deprecated
Proposed change: <human's description of what needs to evolve>
```

### Evo-Step 1: Define the delta

The human describes what needs to change. Classify the change:

| Change type | Description |
|---|---|
| **New scenario** | A new Given/When/Then block to add |
| **Modified scenario** | An existing scenario whose behavior changes |
| **Deprecated scenario** | A scenario that no longer applies |
| **Governing doc change** | A TDR or ADR was updated and the feature must reflect it |

The agent proposes the delta (new/modified/deprecated scenarios) marked as `[AGENT PROPOSAL — awaiting human approval]`. Do NOT touch the rest of the file.

### Evo-Step 2: Delta critique

Critique **only the delta** against the existing `@constraints` baseline and the loaded context:

**New governing docs needed**: Does the delta introduce behavior not covered by any doc in `governed_by`? If so, flag as `[CONTEXT-GAP]`.

**Conflicts with baseline**: Does the delta contradict an existing scenario or a doc in `governed_by`? Flag as `[CONFLICT]`.

**Behavioral gaps in the delta**: Are there edge cases or error states missing from the new/modified scenarios? Flag as `[GAP]`.

**Ambiguities**: Are any steps in the delta unclear? Flag as `[AMBIGUITY]`.

Do NOT re-critique scenarios that are not part of the delta. The baseline is trusted.

### Evo-Step 3: Human decides on the delta

Same decision protocol as Authorship Step 3, scoped to delta items only.

If a `[CONTEXT-GAP]` requires a new TDR or ADR:
1. Agent drafts the doc.
2. Human approves.
3. Agent writes the file and asks the human to reindex it.
4. The new doc is added to `governed_by` in `@constraints`.

### Evo-Step 4: Agent applies the delta

1. Add, modify, or deprecate the scenarios identified in Evo-Step 1.
2. Tag each changed scenario appropriately:
   - New: `@status:new` (will become `@status:implemented` after `acd-session`)
   - Modified: `@status:modified @changed:YYYY-MM-DD @reason:<why>`
   - Deprecated: `@status:deprecated @changed:YYYY-MM-DD @reason:<why>`
3. Update the `@constraints` block only if:
   - New governing docs were added → append to `governed_by`
   - A previously noted conflict was resolved → remove from `conflicts`
   - A new gap was accepted → append to `gaps`
   - A new escalation trigger is identified → append to `escalation_triggers`
4. Do NOT alter `@status:implemented` scenarios that are not part of the delta.

### Evolution output checklist

- [ ] Context loaded from Cliplin MCP
- [ ] Baseline read and summarized (Evo-Step 0)
- [ ] Delta classified by change type (Evo-Step 1)
- [ ] Delta critique produced — only the changed scenarios (Evo-Step 2)
- [ ] Human decisions received on all critical delta items (Evo-Step 3)
- [ ] Delta applied to `.feature` file with correct status tags (Evo-Step 4)
- [ ] `@constraints` block updated only where the delta requires it
- [ ] Human confirmed readiness for implementation

---

## Handoff to implementation (both modes)

After the final step of either mode, confirm with the human:
> "The ADC is complete. `governed_by` references [list docs]. Shall I proceed with implementation using the `acd-session` skill?"

Do not begin implementation without explicit human confirmation.

## References

- `cliplin-acd/tdrs/acd-agent-delivery-contract.md`
- `cliplin-acd/adrs/001-acd-framework.md`
- `cliplin-acd/skills/acd-session/SKILL.md`
