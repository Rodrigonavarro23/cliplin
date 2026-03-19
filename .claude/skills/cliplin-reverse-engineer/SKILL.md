# Skill: cliplin-reverse-engineer

Reverse-engineer a project and guide the user to create Cliplin specs (feature files,
ADRs, TDRs, business docs) from existing code, documentation, and project signals.

---

## Before you start — startup check

1. Check whether `.cliplin/.re-progress.yaml` exists at the project root.
2. If it exists and `modules_pending` is non-empty, present this prompt:

   ```
   Found an in-progress reverse-engineering session from <generated_at>:
     Completed: <modules_completed>
     Current:   <current_module> (Phase <current_phase>)
     Pending:   <modules_pending>

   Options:
     [C] Continue from where it left off
     [R] Restart from the beginning
     [M] Jump to a specific module
   ```

   - **[C]**: reload `context_references` queries against the Cliplin MCP, then resume at `current_module` / `current_phase`.
   - **[R]**: delete `.cliplin/.re-progress.yaml` and start a fresh scan.
   - **[M]**: ask which module to jump to; proceed to Phase 1 for that module.

3. If the file is **malformed** (not valid YAML): emit a warning and proceed as a fresh scan.
   Do NOT delete the malformed file — the user may want to fix it.
4. If the file does not exist: proceed with a fresh scan (no prompt).

If the user invokes the skill targeting a specific module (e.g. "run cliplin-reverse-engineer
on src/payments"), go to **Module targeting** below.

---

## Step 1 — Scan the project

### What to scan

**Always scan (when present):**
- Source tree: non-binary files under `src/`, `lib/`, `app/`, `pkg/`, `internal/`, `cmd/`.
  If none of these exist, scan from project root, excluding hidden dirs,
  `vendor/`, `node_modules/`, `dist/`, `build/`, `.git/`.
- Project manifests: `package.json`, `pyproject.toml`, `setup.py`, `Cargo.toml`,
  `go.mod`, `pom.xml`, `build.gradle`, `composer.json`.
- Documentation: `README.*`, `CHANGELOG.*`, `docs/**/*.md`, `docs/**/*.html`,
  diagram files (`*.mermaid`, `*.puml`, `*.drawio`).
- Existing Cliplin specs: `docs/features/**/*.feature`, `docs/adrs/**/*.md`,
  `docs/tdrs/**/*.md`, `docs/business/**/*.md`, `docs/ts4/**/*.ts4`.
- Test files: **file names and describe/it/test block headings only** under `test/`,
  `tests/`, `spec/`, `__tests__/`. Do NOT read full test bodies.

**Optional (only if available):**
- Git history: run `git log --oneline -50` to understand project evolution.
  Do NOT inspect individual commit diffs. Skip silently if git is unavailable.

**Never scan:**
- Binary files, images, compiled artifacts, databases.
- `vendor/`, `node_modules/`, `.git/`, `dist/`, `build/`, `__pycache__/`, `.venv/`, `venv/`.
- Files larger than 500 KB.

### Empty project guard

After scanning, if **no** source files, manifests, README, docs, or test files were found:

```
This project appears to be empty — no files were found to analyze.
Add source code, a README, or a manifest file and run the skill again.
```

Do NOT create `.cliplin/.re-progress.yaml`. Exit.

---

## Step 2 — Detect top-level modules

1. For each source root found (`src/`, `lib/`, etc.), list its **immediate subdirectories**
   as candidate modules.
2. Include a candidate if it contains at least one: source file, README, test file,
   or manifest reference.
3. If the source root has **no subdirectories**, treat the entire root as one module
   named after the project.
4. Cross-reference with existing feature files: if any `governed_by` entry in existing
   features relates to a module path, mark it `has_existing_specs: true`.

Each module has:
- `module_name`: directory name or inferred name.
- `path`: relative path from project root.
- `has_existing_specs`: true/false.
- `inferred_domain`: short description from file names, manifest keywords, README headings.

---

## Step 3 — Present the process plan

```
Detected N top-level modules:
  1. <module_name> (<path>) — <inferred_domain>  [coverage: existing | partial | none]
  2. ...

I will process each module one at a time:
  Phase 1 — Findings report
  Phase 2 — Guided spec drafting

Shall I start with module 1 (<module_name>)?
```

The user may reorder or skip modules. Do NOT proceed until the user confirms.

Write `.cliplin/.re-progress.yaml` now (see **Tracking file** below).

---

## Step 4 — Per-module: Phase 1 (Findings report)

For the current module, produce:

```
## Module: <module_name>

### Detected domain concepts
  - <entity>: <brief description inferred from code/tests>

### Inferred use cases
  - <use_case>: <trigger> → <outcome>

### Existing coverage
  Feature files: <list or "none">
  ADRs:          <list or "none">
  TDRs:          <list or "none">
  Business docs: <list or "none">

### Findings
  [MISSING-FEATURE]      <name>: No feature file covers this behavior
  [MISSING-TDR]          <area>: No TDR documents this technical constraint
  [MISSING-ADR]          <decision>: No ADR records this architectural choice
  [MISSING-BUSINESS-DOC] <concept>: No business doc defines this domain concept
  [PARTIAL-SPEC]         <file>: Spec exists but lacks @constraints or governed_by

### Context signals beyond code
  - <intent inferred from README, CHANGELOG, git history, or test descriptions
     that the code alone does not reveal>
```

After the report:
> "Phase 1 complete for `<module_name>`. Found N findings. Proceed to Phase 2 (guided drafting)?"

Update `.cliplin/.re-progress.yaml`: set `current_phase: 2`.

---

## Step 5 — Per-module: Phase 2 (Guided spec drafting)

For each finding, in sequence:

1. Announce finding type and name.
2. Propose a draft document marked `[AGENT PROPOSAL — awaiting human approval]`.
3. Wait for human confirmation, rejection, or modification before moving to the next finding.
4. After approval: instruct the user to write the file to the correct path and run
   `cliplin reindex <path>`.

After all findings are resolved:
> "Module `<module_name>` complete. Move to next module?"

Update `.cliplin/.re-progress.yaml`: move `current_module` to `modules_completed`,
advance `current_module` to the next pending module, set `current_phase: 1`.

---

## Step 6 — Completion

When all modules are done:
> "All modules processed. The reverse-engineering session is complete."

Delete `.cliplin/.re-progress.yaml`.

---

## Module targeting

When the user invokes the skill targeting a specific module or path:

1. If a progress file exists: load the module list from it. Look up the requested
   module by name or path (case-insensitive, partial match).
   - If **one match**: jump to Phase 1 for that module.
   - If **multiple matches**: list them and ask the user to choose. Wait for selection.
   - If **no match**: inform the user and list available modules.
2. If **no progress file**: perform a targeted scan of the specified path only.
   Create `.cliplin/.re-progress.yaml` with `modules_total: 1` and
   `invocation_target` set to the module name. Proceed directly to Phase 1.
3. After completing the targeted module, ask:
   > "Module `<module_name>` complete. Do you want to continue with the full project scan?"
   - Yes: rewrite `.cliplin/.re-progress.yaml` with the full module list
     (`modules_total` = real count, `invocation_target: null`, `modules_completed`
     includes the targeted module). Proceed to the next pending module.
   - No: mark the module as completed in the progress file. Do not delete it.

---

## Tracking file format

Maintain `.cliplin/.re-progress.yaml` throughout the session:

```yaml
# cliplin-reverse-engineer progress — delete when complete
generated_at: "<ISO 8601 UTC>"
modules_total: <N>
modules_completed: [<module_name>, ...]
modules_pending: [<module_name>, ...]
current_module: <module_name>
current_phase: <1|2>
invocation_target: "<module_name or null>"
context_references:
  - collection: technical-decision-records
    query: "<last MCP query string used>"
  - collection: features
    query: "<last MCP query string used>"
  - collection: business-and-architecture
    query: "<last MCP query string used>"
```

Rules:
- Write/update at the start of each module and after each phase completes.
- Store only state needed to resume. No proposals, no full content.
- `context_references` stores last MCP query strings for reloading after context compaction.
- Do NOT commit this file. `cliplin init` ensures `.gitignore` covers it.
