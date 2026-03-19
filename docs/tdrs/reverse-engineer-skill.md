---
tdr: "1.0"
id: "reverse-engineer-skill"
title: "cliplin-reverse-engineer Built-in Skill"
summary: "Specification for the cliplin-reverse-engineer skill: scan sources, top-level module detection, startup check with resume capability, module targeting, two-phase per-module guidance flow (findings → guided drafting), tracking file for process continuity, template function, and init-time linking."
---

# rules

## Skill location (MUST)

- The skill lives at `.cliplin/knowledge/cliplin-framework/skills/cliplin-reverse-engineer/SKILL.md`
  inside the built-in framework package.
- It is created by a dedicated template function `create_reverse_engineer_skill(framework_base: Path)`
  in `src/cliplin/utils/templates.py`.
- `create_reverse_engineer_skill` is called from `create_framework_knowledge_package` so it is always
  written on every `cliplin init` or re-init.
- The file MUST be written with `encoding="utf-8"` per docs/tdrs/cliplin-cli-stack.md.

## Skill auto-linking at init time (MUST)

- Same pattern as `cliplin-context-audit` (docs/tdrs/context-audit-skill.md §Skill auto-linking).
- `ClaudeDesktopIntegration.apply()` MUST call `self.link_knowledge_skills(target_dir, framework_base)`
  → skill appears at `.claude/skills/cliplin-reverse-engineer/SKILL.md`.
- `CursorIntegration.apply()` → `.cursor/skills/cliplin-reverse-engineer/SKILL.md`.
- `GeminiCliIntegration.apply()` → `.gemini/skills/cliplin-reverse-engineer/SKILL.md`.
- Re-running `cliplin init` MUST refresh the link (shutil.rmtree + re-link).
- If hard-link creation fails (OSError, cross-filesystem): warn and continue — init MUST NOT fail.

## Scan sources (MUST)

### Mandatory (always scan when present)
- **Source tree**: non-binary files under `src/`, `lib/`, `app/`, `pkg/`, `internal/`, `cmd/`.
  If none of these exist, scan from project root excluding hidden dirs,
  `vendor/`, `node_modules/`, `dist/`, `build/`, `.git/`.
- **Project manifests**: `package.json`, `pyproject.toml`, `setup.py`, `Cargo.toml`,
  `go.mod`, `pom.xml`, `build.gradle`, `composer.json` — whichever are present.
- **Documentation**: `README.*`, `CHANGELOG.*`, `docs/**/*.md`, `docs/**/*.html`,
  any diagram files (`*.mermaid`, `*.puml`, `*.drawio`) anywhere in the project.
- **Existing Cliplin specs**: `docs/features/**/*.feature`, `docs/adrs/**/*.md`,
  `docs/tdrs/**/*.md`, `docs/business/**/*.md`, `docs/ts4/**/*.ts4`.
- **Test files**: file names and describe/it/test block headings under `test/`, `tests/`,
  `spec/`, `__tests__/`. Do NOT read full implementations.

### Optional (scan only if available)
- **Git history**: run `git log --oneline -50` to understand project evolution.
  Do NOT inspect individual commit diffs. Skip silently if git is unavailable.

### Exclusions (never scan)
- Binary files, compiled artifacts, images, databases.
- `vendor/`, `node_modules/`, `.git/`, `dist/`, `build/`, `__pycache__/`, `.venv/`, `venv/`.
- Files larger than 500 KB.

## Empty project guard (MUST)

- After completing the scan, if no source files, manifests, README, docs, or test files
  were found, the skill MUST inform the user and exit cleanly:
  `This project appears to be empty — no files were found to analyze. Add source code,
   a README, or a manifest file and run the skill again.`
- The skill MUST NOT create `.cliplin/.re-progress.yaml` in this case.
- Exit with no error.

## Top-level module detection (MUST)

1. For each source root found, list its **immediate subdirectories** as candidate modules.
2. Include a candidate if it contains at least one: source file, README, test file, or manifest reference.
3. If the source root has no subdirectories, treat the entire root as one module named after the project.
4. Cross-reference with existing feature files: mark modules that already have partial spec coverage.

Each detected module carries:
- `module_name`: directory name or inferred name.
- `path`: relative path from project root.
- `has_existing_specs`: true if any `governed_by` entry in existing features relates to this module.
- `inferred_domain`: short description from file names, manifest keywords, and README headings.

## Startup check (MUST)

On every invocation, before scanning, the skill MUST:

1. Check whether `.cliplin/.re-progress.yaml` exists at the project root.
2. If it exists and `modules_pending` is non-empty, present a resume prompt:

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

3. Wait for explicit user choice before proceeding:
   - **C**: reload `context_references` queries against the MCP, then resume at
     `current_module` / `current_phase`.
   - **R**: delete `.cliplin/.re-progress.yaml` and start a fresh scan.
   - **M**: go to module targeting flow (see §Module targeting).

4. If the file does not exist: proceed with a fresh scan (no prompt).
5. If the file is malformed (unparseable YAML): warn the user, offer to delete it,
   and start fresh.

## Module targeting (MUST)

The skill supports targeting a single module directly, bypassing full project scan:

### Invocation
The user may invoke the skill with a module name or path:
> "Run cliplin-reverse-engineer on module `<module_name>`"
> "Run cliplin-reverse-engineer on `src/payments`"

### Behavior
1. If a progress file exists: load the module list from it. Look up the requested
   module by name or path (case-insensitive, partial match accepted).
   If found, jump directly to Phase 1 for that module.
2. If no progress file exists: perform a **targeted scan** — scan only the specified
   path instead of the full project. Skip the process plan presentation.
   Write/update `.cliplin/.re-progress.yaml` with `modules_total: 1` and
   `current_module` set to the target.
3. After completing the targeted module, ask:
   > "Module `<module_name>` complete. Do you want to continue with the full project scan?"
   - Yes: resume or start the full scan, skipping already-completed modules.
   - No: mark the module as completed in the progress file. Do not delete the file
     (other modules may still be pending).
4. If the requested module name/path does not match any detected module, inform the
   user and list available modules from the progress file (or offer a fresh scan).

## Process plan (MUST)

After detection (or after startup check resolves to a fresh scan), present the plan:

```
Detected N top-level modules:
  1. <module_name> (<path>) — <inferred_domain>  [coverage: existing | partial | none]
  2. ...

I will process each module one at a time:
  Phase 1 — Findings report
  Phase 2 — Guided spec drafting

Shall I start with module 1 (<module_name>)?
```

The user may reorder or skip modules. Proceed only after explicit confirmation.

## Per-module two-phase flow (MUST)

### Phase 1: Module findings report

Produce a structured report for the current module:

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

After the report, ask:
> "Phase 1 complete for `<module_name>`. Found N findings. Proceed to Phase 2 (guided drafting)?"

### Phase 2: Guided spec drafting

For each finding, in sequence:
1. Announce finding type and name.
2. Propose a draft document marked `[AGENT PROPOSAL — awaiting human approval]`.
3. Wait for human confirmation, rejection, or modification.
4. After approval: instruct the user to write the file to the correct path
   and run `cliplin reindex <path>`.
5. Move to the next finding only after the current one is resolved.

After all findings in a module are resolved:
> "Module `<module_name>` complete. Move to next module?"

## Tracking file for process continuity (MUST)

The skill MUST maintain a small tracking file at `.cliplin/.re-progress.yaml`:

```yaml
# cliplin-reverse-engineer progress — delete when complete
generated_at: "<ISO 8601 UTC>"
modules_total: <N>
modules_completed: [<module_name>, ...]
modules_pending: [<module_name>, ...]
current_module: <module_name>
current_phase: <1|2>
invocation_target: "<module_name or null>"   # set when skill was invoked on a single module
context_references:
  - collection: technical-decision-records
    query: "<last MCP query string used>"
  - collection: features
    query: "<last MCP query string used>"
  - collection: business-and-architecture
    query: "<last MCP query string used>"
```

Rules:
- Write/update the file at the start of each module and after each phase completes.
- Store only state needed to resume: no proposals, no full content.
- `context_references` holds the last MCP query strings so the agent can re-issue them
  after a context compaction without asking the user to repeat context.
- At process completion (all modules done), the skill instructs the AI to delete the file.
- `.cliplin/.re-progress.yaml` MUST NOT be committed. The `cliplin init` command is
  responsible for ensuring `.gitignore` covers this file (see §.gitignore handling below).

### Malformed progress file (MUST)

- If `.cliplin/.re-progress.yaml` exists but cannot be parsed as valid YAML, the skill
  MUST emit a warning and proceed as a fresh start (same as if no file existed):
  `Warning: .cliplin/.re-progress.yaml is malformed and will be ignored. Fix it manually
   and re-run the skill to resume, or a fresh scan will start now.`
- The skill MUST NOT delete or overwrite the malformed file automatically — the user
  may want to inspect and fix it.
- A fresh scan writes a new `.re-progress.yaml`, replacing the malformed one only when
  the first module starts processing.

### Targeted → full scan transition (MUST)

- When the user chooses to continue with the full scan after a targeted module run,
  the skill MUST rewrite `.cliplin/.re-progress.yaml` with:
  - `modules_total` set to the real count of all detected modules.
  - `modules_completed` including the already-processed targeted module.
  - `modules_pending` containing all remaining modules in detection order.
  - `invocation_target` reset to `null`.
- This rewrite happens before Phase 1 of the first full-scan module begins.

### Ambiguous module targeting (MUST)

- When the user invokes the skill targeting a name or path that matches more than one
  detected module (case-insensitive partial match), the skill MUST list all matching
  options and ask the user to choose:
  ```
  Ambiguous target "<input>". Matching modules:
    1. <module_name_A> (<path_A>)
    2. <module_name_B> (<path_B>)
  Which module do you want to process?
  ```
- Proceed only after explicit user selection.

## .gitignore handling at init time (MUST)

- `cliplin init` MUST ensure `.cliplin/.re-progress.yaml` is excluded from version control.
- After writing the framework knowledge package, `cliplin init` MUST:
  1. Check whether a `.gitignore` file exists at the project root.
  2. If it does, check whether `.cliplin/.re-progress.yaml` or `.cliplin/` is already listed.
  3. If not already covered, append the following entry to `.gitignore`:
     ```
     # cliplin-reverse-engineer progress file
     .cliplin/.re-progress.yaml
     ```
  4. If `.gitignore` does not exist, create it with that entry.
- This ensures the tracking file is never accidentally committed regardless of whether
  the user has an existing `.gitignore`.

## feature-template-mapping update (MUST)

- `docs/features/reverse-engineer.feature` → `create_reverse_engineer_skill` in
  `src/cliplin/utils/templates.py`.
- Record this mapping in `docs/tdrs/feature-template-mapping.md` under
  "Known feature ↔ template mappings".
- Any change to `reverse-engineer.feature` scenarios MUST be reflected in
  `create_reverse_engineer_skill`.

code_refs:
  - "src/cliplin/utils/templates.py"
  - "src/cliplin/utils/ai_host_integrations/claude_desktop.py"
  - "src/cliplin/utils/ai_host_integrations/cursor.py"
  - "src/cliplin/utils/ai_host_integrations/gemini_cli.py"
  - ".cliplin/knowledge/cliplin-framework/skills/cliplin-reverse-engineer/SKILL.md"
  - "docs/tdrs/feature-template-mapping.md"
  - "docs/tdrs/context-audit-skill.md"
  - "docs/tdrs/ai-host-integration.md"
  - "docs/tdrs/claude-desktop-integration.md"
  - "docs/tdrs/gemini-integration.md"
  - "docs/tdrs/cliplin-cli-stack.md"
