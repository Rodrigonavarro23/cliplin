---
tdr: "1.0"
id: "cliplin-flow"
title: "Cliplin operational flow: feature-first"
summary: "The feature file is always the source of truth; on any change or request, update the feature spec first if needed, then implement code to fulfill the specs."
---

# rules

## Feature file as source of truth (MUST)

- For Cliplin to work correctly, the feature file (.feature in docs/features/) must always be the source of truth for what the system does
- If a feature does not exist, the functionality does not exist; any new or changed behavior must be reflected in a feature spec

## Spec before code (MUST)

- On any user change or request (new behavior, fix, refactor, enhancement), the first step is to consider whether the feature spec needs to change
- If the spec must change: update (or create) the relevant .feature file first, before modifying code, TS4, ADRs, or any other file
- Only after the feature spec is updated or confirmed should refactors or new code be executed; all code must fulfill the specs

## Planning phase: write constraints before implementing (MUST)

- After loading context from the MCP context store and before starting any implementation, write the `@constraints` block in the feature file
- The `@constraints` block records: which TDRs/ADRs govern the feature (`governed_by`), conflicts detected between documents (`conflicts`), and gaps or unspecified behaviors (`gaps`)
- This block is the tangible output of context loading — it must not remain only in the AI's conversation memory
- A feature file with a complete `@constraints` block is considered planning-complete and ready for implementation
- See docs/tdrs/feature-constraints-format.md for the exact format and field definitions

## AI and human workflow

- When assisting: suggest modifying the feature spec first when the request implies new or changed behavior; then implement to satisfy the spec
- Never change code first and leave the feature file missing or out of date; every change must be traceable to a specification
- Always write the `@constraints` block after context loading and before implementation; never skip the planning phase
- Reference: docs/business/framework.md (Feature-first flow), docs/adrs/000-cliplin-framework.md (Operational flow: feature-first)
code_refs:
  - "docs/features/"
  - "docs/business/framework.md"
  - "docs/adrs/000-cliplin-framework.md"
  - "docs/tdrs/feature-constraints-format.md"
  - ".cursor/rules/feature-first-flow.mdc"
