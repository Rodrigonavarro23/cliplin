---
tdr: "1.0"
id: "cross-references-on-evolution"
title: "Cross-Project Reference Update on Feature or Solution Evolution"
summary: "When creating or evolving a feature or solution, search the project for all references to the same concepts, entities, or contracts and update them so the project stays consistent."
---

# rules

## When you create or evolve a feature, solution, or contract (MUST)

- Identify the concepts, entities, names, or behavioral contracts that changed or were introduced (e.g. a new capability name, a renamed MCP, a new config path, a terminology change like "context store" vs "ChromaDB", a new scenario or step).
- Search the **entire project** for references to those same concepts, entities, or contracts.
- Update every reference so the project stays consistent: same terminology, same behavior description, same config paths, same step wording where the contract is shared.

## Where to search for references (cross-project)

- **Features**: docs/features/*.feature — other features that mention the same capability, entity, or flow (e.g. cli.feature and mcp-storage.feature both refer to context store / MCP).
- **Documentation**: README.md, docs/business/*.md, docs/adrs/*.md — any doc that describes the same capability or user flow.
- **Technical specs**: docs/tdrs/*.md — specs that reference the same contracts, config paths, or naming. For host-specific changes (Cursor, Claude Desktop), update the corresponding docs/tdrs/cursor-integration.md or docs/tdrs/claude-desktop-integration.md.
- **Templates and generated content**: src/cliplin/utils/templates.py and src/cliplin/utils/ai_host_integrations/ (strings that become .cursor/rules/*.mdc, .claude/rules/*.md, .mcp.json, instructions) — must stay aligned with what features and docs say.
- **Cursor/Claude rules**: .cursor/rules/*.mdc, and any generated .claude/rules — rules that instruct AI or users about the same capability.
- **Code that emits user-facing text**: CLI messages, error strings, help text in src/cliplin/ — should match the terminology and behavior described in features and docs.

## Apply this on

- **New feature**: Before closing the work, search for existing features, docs, and templates that describe the same domain or capability and add or adjust references so they stay aligned.
- **Feature evolution**: When you change scenarios, steps, or acceptance criteria, search for other features, docs, templates, and rules that still refer to the old wording or behavior and update them.
- **Solution or contract change**: When you change a contract (e.g. "context store" vs "ChromaDB"), config path, MCP name, or capability name, search all of the above and update every occurrence so nothing is left pointing at the old contract or name.

## Feature ↔ template verification (MUST)

- When modifying a .feature file, consult docs/tdrs/feature-template-mapping.md. If the feature has a template reflection (e.g. knowledge.feature ↔ create_knowledge_packages_adr), you MUST verify and update the corresponding template function in src/cliplin/utils/templates.py so generated content matches the feature spec. Do not leave templates out of sync with features.

## Checklist before considering a feature or solution evolution complete

- [ ] Searched docs/features/ for other features that reference the same capability or entity; updated or added references as needed.
- [ ] Searched README.md and docs/ (business, adrs) for descriptions of the same capability; updated wording to match.
- [ ] Searched docs/tdrs/ for specs that reference the same contract or naming; updated if needed.
- [ ] **Feature ↔ template**: If the modified feature has a template reflection (docs/tdrs/feature-template-mapping.md), verified and updated src/cliplin/utils/templates.py so generated content matches the feature spec.
- [ ] If templates or generated rules describe the same capability (e.g. MCP, context store), searched src/cliplin/utils/templates.py, src/cliplin/utils/ai_host_integrations/, and .cursor/rules (and .claude output) and updated so they stay in sync with features and docs.
- [ ] **`@constraints` blocks**: If a TDR or ADR that is referenced in `governed_by` of any feature's `@constraints` block changed, updated the affected blocks (add new doc to governed_by, remove resolved gaps, note new conflicts if any).
- [ ] Reindexed any modified context files (e.g. cliplin reindex) so the context store index stays current.
- [ ] If changing knowledge package format (cliplin.yaml knowledge section), layout (.cliplin/knowledge/), or reindex rules for packages: updated docs/adrs/005-knowledge-packages.md, docs/tdrs/knowledge-packages.md, docs/tdrs/knowledge-reindex-context.md, docs/features/knowledge.feature, and docs/tdrs/system-modules.md (and docs/tdrs/claude-desktop-integration.md if skills behavior changes).
code_refs:
  - "docs/features/"
  - "docs/adrs/"
  - "docs/business/"
  - "docs/tdrs/"
  - "docs/tdrs/feature-template-mapping.md"
  - "src/cliplin/utils/templates.py"
  - "src/cliplin/utils/ai_host_integrations/"
  - ".cursor/rules/"
