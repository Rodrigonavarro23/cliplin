# Skill: cliplin-context-audit

Analyse the context health of a Cliplin project and output a single JSON object to stdout.

## Instructions

1. **Scan `docs/features/`** for all `.feature` files.  If the directory does not exist, treat `features_total` as 0 and proceed to output.

2. **Parse `@constraints` blocks** from each feature file.
   - A `@constraints` block is the block that begins with the line `@constraints` (before `Feature:`) and continues with YAML comment lines (`# key: value / list`).
   - Parse the YAML comment lines to extract `governed_by`, `gaps`, and `conflicts` lists.
   - Also scan for scenario-level `@constraints` blocks (placed immediately before a `Scenario:` line) and include their `governed_by`, `gaps`, and `conflicts` entries in the aggregation.
   - If a `@constraints` block is malformed or unparseable, skip it and continue (do not abort).

3. **Compute each output field** as follows:

   ### features_total
   Count of `.feature` files found in `docs/features/`.

   ### features_with_constraints
   Count of `.feature` files that contain a `@constraints` block with a **non-empty** `governed_by` list (at least one entry).  A `@constraints` block whose `governed_by` list is empty (`[]`) does NOT count.

   ### gaps
   Collect every entry from every `# gaps:` list in every `@constraints` block across all feature files.  Deduplicate by case-insensitive trim.  Each entry is the plain string as written in the feature file.

   ### conflicts
   Collect every entry from every `# conflicts:` list in every `@constraints` block across all feature files.  Deduplicate by case-insensitive trim.  Each entry is the plain string as written in the feature file.

   ### context_drift
   For each entry in every `governed_by` list, check whether the referenced file exists at that path relative to the project root.  If the file does **not** exist, add a drift entry of the form:
   ```
   "<feature-file> references <governed_by_path> which does not exist"
   ```
   Deduplicate.

   ### dead_documentation
   List every `.md` and `.ts4` file found under `docs/adrs/`, `docs/tdrs/`, and `docs/business/` that is **not** referenced by any `governed_by` entry in any `@constraints` block across the whole project.
   A file is "referenced" if its relative path from the project root appears verbatim in at least one `governed_by` list.
   **Do NOT include `.feature` files** in `dead_documentation` — feature files are the source of truth and are never orphaned documentation.

   ### context_score
   Start at **100**.  Apply the following deductions (apply each category cap before summing):

   | Issue | Deduction per item | Category cap |
   |---|---|---|
   | Feature file missing `@constraints` block (or `governed_by` is empty) | `floor(40 / max(features_total, 1))` | 40 points total |
   | Unique gap entry | 2 points | 20 points total |
   | Unique conflict entry | 5 points | 20 points total |
   | `context_drift` item | 3 points | 15 points total |
   | `dead_documentation` item | 1 point | 10 points total |

   After all deductions, clamp the result: **minimum 0, maximum 100**.

   **Example calculation** (4 feature files, 2 missing `@constraints`, 3 gaps, 1 conflict, 0 drift, 2 dead docs):
   - missing constraints: `floor(40/4) * 2 = 20` (cap 40 → 20 used)
   - gaps: `3 * 2 = 6` (cap 20 → 6 used)
   - conflicts: `1 * 5 = 5` (cap 20 → 5 used)
   - drift: 0
   - dead docs: `2 * 1 = 2` (cap 10 → 2 used)
   - total deduction: 33 → score = 100 − 33 = **67**

4. **Output a single JSON object to stdout**.  No other text, no prose, no markdown fences.  The JSON MUST be valid and parseable (no trailing commas, no comments).

5. **Exit with code 0 always** — even for an empty project or missing `docs/features/` directory.

## Output JSON schema

All fields MUST be present even when their values are zero or empty arrays.

```json
{
  "generated_at": "<ISO 8601 datetime, UTC, e.g. 2026-03-18T10:00:00Z>",
  "project_root": "<absolute path to the project root>",
  "context_score": 100,
  "features_total": 0,
  "features_with_constraints": 0,
  "gaps": [],
  "conflicts": [],
  "context_drift": [],
  "dead_documentation": []
}
```

Field notes:
- `generated_at`: UTC datetime in ISO 8601 format (e.g. `2026-03-18T10:00:00Z`).
- `project_root`: absolute path to the directory that contains `docs/` and `.cliplin/`.
- `context_score`: integer 0–100 (never fractional, never negative, never above 100).
- `features_total`: non-negative integer.
- `features_with_constraints`: non-negative integer ≤ `features_total`.
- `gaps`, `conflicts`, `context_drift`, `dead_documentation`: arrays of strings (deduplicated).

No additional fields are permitted.  No `risk` label.  No `pass`/`fail` field.  The consumer decides what constitutes a problem based on the raw numbers.
