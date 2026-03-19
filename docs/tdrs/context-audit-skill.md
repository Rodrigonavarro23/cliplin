---
tdr: "1.0"
id: "context-audit-skill"
title: "cliplin-context-audit Built-in Skill"
summary: "Specification for the cliplin-context-audit skill: its location inside the cliplin-framework knowledge package, the template function that creates it, the JSON stdout schema it produces, how it is linked at init time, and the computation rules for each output field."
---

# rules

## Skill location (MUST)

- The skill lives at `.cliplin/knowledge/cliplin-framework/skills/cliplin-context-audit/SKILL.md` inside the built-in framework package.
- It is created by a dedicated template function `create_context_audit_skill(framework_base: Path)` in `src/cliplin/utils/templates.py`.
- `create_context_audit_skill` is called from `create_framework_knowledge_package` so it is always written on every `cliplin init` or re-init.
- The file MUST be written with `encoding="utf-8"` per the cross-platform file-operations rule (docs/tdrs/cliplin-cli-stack.md).

## Skill auto-linking at init time (MUST)

- When `cliplin init --ai claude-code` (or alias `claude-desktop`) runs, after `create_framework_knowledge_package` completes, the `ClaudeDesktopIntegration` handler MUST call `link_knowledge_skills(project_root, framework_base)` on itself so that the skill appears at `.claude/skills/cliplin-context-audit/SKILL.md`.
- When `cliplin init --ai cursor` runs, the `CursorIntegration` handler MUST call `link_knowledge_skills(project_root, framework_base)` so that the skill appears at `.cursor/skills/cliplin-context-audit/SKILL.md`.
- The framework package does NOT appear in `cliplin.yaml` (it is hidden), so the normal `cliplin knowledge add` code path is NOT used for skill linking; init is the only time these links are created for the framework package.
- The `link_knowledge_skills` method already implements the correct hard-link logic (see docs/tdrs/claude-desktop-integration.md); no new linking code is required — only a new call site is needed.
- **Call site MUST be each integration handler's `apply()` method** (not `create_framework_knowledge_package`): `create_framework_knowledge_package` does not receive the AI host identifier and cannot call host-specific methods. Each handler (e.g. `ClaudeDesktopIntegration.apply`, `CursorIntegration.apply`) MUST call `self.link_knowledge_skills(target_dir, framework_base)` after `create_framework_knowledge_package(target_dir)` completes. `framework_base` is `target_dir / ".cliplin" / "knowledge" / FRAMEWORK_PACKAGE_DIR`.
- Re-running `cliplin init` MUST refresh the link (existing link is removed and recreated) because `link_knowledge_skills` already calls `shutil.rmtree` on the destination folder before re-linking.
- When `cliplin init --ai gemini` runs, after `create_framework_knowledge_package` completes, the `GeminiCliIntegration` handler MUST call `link_knowledge_skills(project_root, framework_base)` so that the skill appears at `.gemini/skills/cliplin-context-audit/SKILL.md`.
- If a host does not support skills and has no `link_knowledge_skills` method on the integration, no action is taken; the absence of the method is the signal that the host does not support them.
- If the hard-link creation fails at init time (e.g. `OSError`, cross-filesystem): **warn and continue** — init MUST NOT fail because of a skill link failure. Log a warning to stderr and proceed. The skill will not be available in the host but the project is still usable.

## JSON stdout output schema (MUST)

- The skill instructs the AI to output a single JSON object to stdout. No file is written. The consumer (human, script, CI) receives the JSON on stdout.
- The schema is fixed. All fields MUST be present even when their values are empty:

```json
{
  "generated_at": "<ISO 8601 datetime, UTC, e.g. 2026-03-18T10:00:00Z>",
  "project_root": "<absolute path to the project root>",
  "context_score": <integer 0–100>,
  "features_total": <integer>,
  "features_with_constraints": <integer>,
  "gaps": ["<gap description>", ...],
  "conflicts": ["<conflict description>", ...],
  "context_drift": ["<drift description>", ...],
  "dead_documentation": ["<file path>", ...]
}
```

- No risk labels, no thresholds, no pass/fail field. `context_score` is a raw integer; the consumer decides what constitutes a problem.
- Empty store or no features found: output the same schema with integer fields set to 0 and array fields set to `[]`. This is not an error.
- The JSON MUST be valid and parseable. No trailing commas. No comments in output.

## context_score computation (MUST)

- `context_score` is 0–100 and measures how well the project context is specified.
- Base formula: start at 100. Deduct points for each issue found:
  - Each feature file missing a `@constraints` block: deduct `floor(40 / max(features_total, 1))` points (capped so total deduction from this category ≤ 40).
  - Each gap found across all `@constraints` blocks: deduct 2 points per gap (total deduction from gaps ≤ 20).
  - Each conflict found across all `@constraints` blocks: deduct 5 points per conflict (total deduction from conflicts ≤ 20).
  - Each `context_drift` item: deduct 3 points per item (total deduction from drift ≤ 15).
  - Each `dead_documentation` item: deduct 1 point per item (total deduction from dead docs ≤ 10).
- Minimum score: 0. Maximum: 100.
- The AI MUST show its work in the SKILL.md instructions so an implementer can reproduce the same number.

## gaps field (MUST)

- Collect all `# gaps:` entries from `@constraints` blocks across all `.feature` files in `docs/features/`.
- Deduplicate identical strings (case-insensitive trim).
- Each entry is a plain string describing the gap as written in the feature file.

## conflicts field (MUST)

- Collect all `# conflicts:` entries from `@constraints` blocks across all `.feature` files in `docs/features/`.
- Deduplicate identical strings (case-insensitive trim).
- Each entry is a plain string describing the conflict as written in the feature file.

## context_drift field (MUST)

- `context_drift` describes governing documents listed in `governed_by` blocks that no longer exist on disk.
- For each `governed_by` entry in each `@constraints` block, check whether the referenced file exists at the path relative to project root.
- If the file does not exist, add a drift entry of the form: `"<feature-file> references <governed_by_path> which does not exist"`.
- Deduplicate.

## dead_documentation field (MUST)

- `dead_documentation` lists `.md` and `.ts4` files from `docs/adrs/`, `docs/tdrs/`, and `docs/business/` that are NOT referenced by any `governed_by` entry in any `@constraints` block and are NOT a known framework file.
- `.feature` files are NEVER included in `dead_documentation`. Feature files are the primary spec artifacts and source of truth; they govern TDRs and ADRs, not the other way around. Including them would invert the dependency relationship.
- Known framework files (excluded from dead_documentation): files under `.cliplin/knowledge/cliplin-framework/`.
- A file is considered "referenced" if its relative path (from project root) appears verbatim in at least one `governed_by` list anywhere in the project's feature files.
- Purpose: surfaces auxiliary documentation (TDRs, ADRs, business docs) that may be out of date or orphaned (no feature explicitly depends on it).

## features_with_constraints field (MUST)

- Count of `.feature` files in `docs/features/` that contain a `@constraints` block with a non-empty `governed_by` list (at least one entry).
- A `@constraints` block with `governed_by: []` is NOT counted as having constraints.

## Skill SKILL.md content requirements (MUST)

- The SKILL.md file MUST instruct the AI to:
  1. Scan `docs/features/` for all `.feature` files.
  2. Parse each `@constraints` block (feature-level and scenario-level) to extract `governed_by`, `gaps`, and `conflicts` entries.
  3. Compute all output fields per the rules in this TDR.
  4. Output the result as a single JSON object to stdout. No other output.
  5. Exit with code 0 always (even for empty store or missing docs).
- The SKILL.md MUST include the full JSON schema as a reference for the AI.
- The SKILL.md MUST explain the `context_score` formula so the AI can reproduce it.

## Template function (MUST)

- `create_context_audit_skill(framework_base: Path)` in `src/cliplin/utils/templates.py`:
  - Creates the directory `framework_base / "skills" / "cliplin-context-audit"`.
  - Writes `SKILL.md` to that directory with the content defined by this TDR.
  - Uses `encoding="utf-8"` for all file writes.
  - Called from `create_framework_knowledge_package` after the ADR creation calls.

## feature-template-mapping update (MUST)

- `docs/features/context-audit.feature` has a template reflection: `create_context_audit_skill` in `src/cliplin/utils/templates.py`.
- This mapping MUST be recorded in `docs/tdrs/feature-template-mapping.md` under "Known feature ↔ template mappings".
- Any change to `context-audit.feature` scenarios (e.g. new output field, new computation rule) MUST be reflected in `create_context_audit_skill` in templates.py.

code_refs:
  - "src/cliplin/utils/templates.py"
  - "src/cliplin/utils/ai_host_integrations/claude_desktop.py"
  - "src/cliplin/utils/ai_host_integrations/cursor.py"
  - "src/cliplin/utils/ai_host_integrations/gemini_cli.py"
  - ".cliplin/knowledge/cliplin-framework/skills/cliplin-context-audit/SKILL.md"
  - "docs/tdrs/feature-template-mapping.md"
  - "docs/tdrs/knowledge-packages.md"
  - "docs/tdrs/ai-host-integration.md"
  - "docs/tdrs/claude-desktop-integration.md"
  - "docs/tdrs/gemini-integration.md"
  - "docs/tdrs/cliplin-cli-stack.md"
