---
tdr: "1.0"
id: "feature-constraints-format"
title: "Feature Constraints Block Format"
summary: "Convention for embedding a @constraints block in .feature files that records which ADRs/TDRs govern a feature, detected conflicts, and gaps identified during planning — before implementation begins."
---

# rules

## Purpose (MUST understand)

- The `@constraints` block is the tangible output of the context loading phase: it records what was found before implementation starts, so it is not lost between sessions
- It enables a planning gate: after loading context and before writing any code, the AI writes the constraints block and the developer can review it
- It provides traceability: anyone reading the feature file later knows which docs governed the implementation and what gaps were accepted

## Format (MUST follow)

- Use the Gherkin tag `@constraints` as the start marker, placed immediately before `Feature:` (feature-level) or immediately before `Scenario:` (scenario-level)
- Each constraint field is written as a YAML comment: every line prefixed with `# `
- End is implicit: the block ends at the next Gherkin keyword (`Feature:`, `Background:`, `Scenario:`, or another tag)
- This format is 100% valid Gherkin and is ignored by BDD test runners; the AI reads it as structured text

## Fields

- **`governed_by`** (list of file paths): TDRs, ADRs, and business docs that actively govern the implementation of this feature or scenario. Use relative paths from project root.
- **`conflicts`** (list of strings): Contradictions detected between two or more governing documents. Describe the conflict clearly.
- **`gaps`** (list of strings): Behaviors or edge cases that are assumed but not explicitly specified in any governing document.
- **`assumptions`** (list of strings, optional): Decisions made to fill gaps. Useful when a gap was resolved by a conscious decision rather than left open.

## Feature-level example

```gherkin
@constraints
# governed_by:
#   - docs/tdrs/cliplin-flow.md
#   - docs/adrs/000-cliplin-framework.md
#   - docs/tdrs/feature-constraints-format.md
# conflicts:
#   - "cliplin-flow.md requires spec before code but does not define what to do when the feature file does not exist yet"
# gaps:
#   - "No spec for reindex behavior when the context store is unavailable"
Feature: Cliplin CLI Tool
  As a developer...
```

## Scenario-level example

Use scenario-level `@constraints` only when a scenario has constraints that differ from the feature-level ones.

```gherkin
  @constraints
  # governed_by:
  #   - docs/tdrs/auth.md
  # gaps:
  #   - "No spec for expired token during login"
  @status:pending
  Scenario: User logs in with OAuth
    Given the user has an active account
```

## When to write the block

- **Feature-level**: After context loading (phase 0), before starting feature analysis (phase 1). Write it once per feature file, unless there are scenario-specific constraints.
- **Scenario-level**: Only when a specific scenario has constraints that do not apply to the rest of the feature (edge cases, special rules, local conflicts).

## When to update the block

- When a governing TDR or ADR is modified and the change affects this feature
- When a new conflict or gap is discovered during implementation
- When a gap is resolved by a new TDR/ADR (remove from gaps, add the new doc to governed_by)

## Tag order convention

At feature level, `@constraints` goes first, before any other feature-level tags.
At scenario level, `@constraints` goes first, before `@status:*` and other scenario tags.

## Relationship to the spec-first flow

- The `@constraints` block is part of the spec, not part of the code
- It does NOT replace TDRs, ADRs, or the feature scenarios — it references them
- A feature file with a complete `@constraints` block is considered "planning-complete" and ready for implementation

code_refs:
  - "docs/features/"
  - "docs/tdrs/cliplin-flow.md"
  - ".claude/rules/feature-processing.md"
  - ".cursor/rules/feature-processing.mdc"
