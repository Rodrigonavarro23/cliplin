# Skill: acd-commit-validator

Validate staged changes against ACD rules before a commit is finalized. Designed to run as a pre-commit hook or on demand. Produces a structured PASS/FAIL report with specific violations.

## When to use this skill

Use this skill:
- **As a pre-commit hook**: automatically on every `git commit` to gate non-compliant commits.
- **On demand**: when you want to verify staged changes before committing.

Do NOT use this skill to validate already-merged PRs or to audit historical commits.

## Hook installation

This skill ships with canonical shell scripts and a `pre-commit` framework configuration. When invoked in a project that does not yet have ACD hooks installed, the agent MUST detect this and offer to install them.

### Detection: does the project have ACD hooks?

Check for the presence of **any** of these signals:
- `scripts/acd-validate.sh` exists
- `scripts/acd-validate-msg.sh` exists
- `.pre-commit-config.yaml` contains `acd-commit-validator`

If none of these exist, the project does NOT have ACD hooks installed. Go to **Installation offer**.

### Installation offer

Ask the human:
> "This project does not have ACD hooks installed. Do you want me to create `scripts/acd-validate.sh`, `scripts/acd-validate-msg.sh`, and `.pre-commit-config.yaml` to enable automatic validation on every commit?"

If the human confirms, **detect the AI CLI before generating the scripts**:

#### AI CLI detection (run before creating any file)

1. Check which known AI CLIs are available in the environment:
   - Run `command -v claude` — Claude Code CLI
   - Run `command -v gemini` — Gemini CLI
   - Run `command -v ai` — generic fallback
   - Add others as they become relevant

2. Based on results:
   - **None found**: stop and tell the human: "No AI CLI found in PATH. Install one (e.g. Claude Code) or set `ACD_AI_BIN` before retrying."
   - **Exactly one found**: use it automatically. Announce: "Detected `<binary>` — scripts will use it as the AI backend."
   - **Multiple found**: ask the human: "I found these AI CLIs: `<list>`. Which one should the ACD hooks use?"

3. Each CLI has a known invocation pattern. Use the one that matches the selected CLI:

| CLI binary | Invocation pattern |
|---|---|
| `claude` | `echo "$PROMPT" \| claude --print --allowedTools "Bash,Read,Glob,Grep"` |
| `gemini` | `echo "$PROMPT" \| gemini --prompt -` |
| unknown | `echo "$PROMPT" \| <binary> --print` (fallback; may need manual adjustment) |

Store the selected binary as `ACD_AI_BIN` and its invocation pattern as a shell function `run_ai()` in the generated scripts (see templates below).

---

If the human confirms installation:

1. **Create `scripts/acd-validate.sh`** (pre-commit stage) — substitute `<ACD_AI_BIN>` and `<run_ai body>` with the detected values:

```bash
#!/usr/bin/env bash
# ACD Commit Validator — pre-commit stage.
# Validates staged artifacts, test coverage, and traceability (AC-*, UD-1, TR-*).
# UD-2 (commit message format) is handled by the separate commit-msg hook.
# Exits 0 (PASS) or 1 (FAIL).
#
# AI CLI: configured at install time. Override with ACD_AI_BIN env var.

ACD_AI_BIN="${ACD_AI_BIN:-<detected-binary>}"

if ! command -v "$ACD_AI_BIN" &>/dev/null; then
  echo "[ACD] ERROR: AI CLI '$ACD_AI_BIN' not found. Set ACD_AI_BIN to the correct binary." >&2
  exit 1
fi

# Adapter: invoke the AI CLI with the prompt. Adjust if you switch AI tools.
run_ai() {
  local prompt="$1"
  # <insert invocation pattern for detected CLI here>
  # Example for claude:  echo "$prompt" | "$ACD_AI_BIN" --print --allowedTools "Bash,Read,Glob,Grep"
  # Example for gemini:  echo "$prompt" | "$ACD_AI_BIN" --prompt -
}

# If nothing is staged, skip validation.
STAGED=$(git diff --cached --name-only 2>/dev/null)
if [ -z "$STAGED" ]; then
  echo "[ACD] No staged files — skipping validation." >&2
  exit 0
fi

echo "[ACD] Running acd-commit-validator (pre-commit stage) on staged files:" >&2
echo "$STAGED" | sed 's/^/  /' >&2

PROMPT="Run the acd-commit-validator skill on the current staged changes. Use 'git diff --cached --name-only' and 'git diff --cached --stat' to see what is staged. Do NOT check UD-2 (commit message format) — that is handled by a separate commit-msg hook. Focus on: AC-1 (feature coverage), AC-2 (@constraints block), AC-3 (governed_by paths exist), AC-4 (scenario status), UD-1 (tests present), UD-3 (branch warning), TR-1 (orphan code), TR-2 (WIP marker). For infra-only commits (no .go/.ts/.py production files staged), pass AC-1, UD-1 and TR-1 automatically. Produce the full structured report and end with exactly ACD-VALIDATION: PASS or ACD-VALIDATION: FAIL."

OUTPUT=$(run_ai "$PROMPT" 2>&1) || true

echo "$OUTPUT"

if echo "$OUTPUT" | grep -q "ACD-VALIDATION: PASS"; then
  exit 0
else
  echo "" >&2
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >&2
  echo "Commit blocked by ACD pre-commit validator." >&2
  echo "Fix the violations above and retry." >&2
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >&2
  exit 1
fi
```

2. **Create `scripts/acd-validate-msg.sh`** (commit-msg stage):

```bash
#!/usr/bin/env bash
# ACD Commit Validator — commit-msg stage.
# Validates UD-2: commit message format (ACD-session, Artifacts, Scenarios fields).
# Receives the path to the commit message file as $1.
# Exits 0 (PASS) or 1 (FAIL).
#
# AI CLI: configured at install time. Override with ACD_AI_BIN env var.

ACD_AI_BIN="${ACD_AI_BIN:-<detected-binary>}"
COMMIT_MSG_FILE="${1:-}"

if ! command -v "$ACD_AI_BIN" &>/dev/null; then
  echo "[ACD] ERROR: AI CLI '$ACD_AI_BIN' not found. Set ACD_AI_BIN to the correct binary." >&2
  exit 1
fi

# Adapter: invoke the AI CLI with the prompt. Adjust if you switch AI tools.
run_ai() {
  local prompt="$1"
  # <insert invocation pattern for detected CLI here>
}

if [ -z "$COMMIT_MSG_FILE" ] || [ ! -f "$COMMIT_MSG_FILE" ]; then
  echo "[ACD] ERROR: commit message file not found at '$COMMIT_MSG_FILE'." >&2
  exit 1
fi

COMMIT_MSG=$(cat "$COMMIT_MSG_FILE")

# Infrastructure-only skip: if message contains [skip-UD-2], pass.
if echo "$COMMIT_MSG" | grep -q "\[skip-UD-2\]"; then
  echo "[ACD] UD-2 skipped via [skip-UD-2] marker." >&2
  exit 0
fi

echo "[ACD] Validating commit message format (UD-2)..." >&2

PROMPT="Check this commit message for ACD UD-2 compliance. The message must contain: an 'ACD-session:' line, an 'Artifacts:' line, and a 'Scenarios:' line. If all three are present, output 'ACD-VALIDATION: PASS'. If any are missing, list which ones and output 'ACD-VALIDATION: FAIL'. Commit message: $(echo "$COMMIT_MSG" | head -20)"

OUTPUT=$(run_ai "$PROMPT" 2>&1) || true

echo "$OUTPUT"

if echo "$OUTPUT" | grep -q "ACD-VALIDATION: PASS"; then
  exit 0
else
  echo "" >&2
  echo "[ACD] UD-2 fix: add 'ACD-session:', 'Artifacts:', and 'Scenarios:' lines." >&2
  echo "[ACD]   Or add [skip-UD-2] with a justification for infra-only commits." >&2
  exit 1
fi
```

3. **Create or merge `.pre-commit-config.yaml`**:

If the file does not exist, create it. If it exists and already has a `repos:` block, add the `acd-commit-validator` and `acd-commit-msg-validator` hooks under the `local` repo entry (create that entry if missing).

```yaml
repos:
  - repo: local
    hooks:
      - id: acd-commit-validator
        name: ACD Commit Validator (artifacts + tests + traceability)
        language: script
        entry: scripts/acd-validate.sh
        pass_filenames: false
        always_run: true
        stages: [pre-commit]
        description: >
          Validates staged changes against ACD rules: artifact consistency (AC-1–4),
          test coverage (UD-1), and traceability (TR-1–2). Blocks the commit on
          any FAIL violation. Infra-only commits (no production .go/.ts/.py files)
          pass AC-1, UD-1, and TR-1 automatically.

      - id: acd-commit-msg-validator
        name: ACD Commit Message Validator (UD-2)
        language: script
        entry: scripts/acd-validate-msg.sh
        pass_filenames: true
        stages: [commit-msg]
        description: >
          Validates that the commit message contains the required ACD fields:
          ACD-session, Artifacts, and Scenarios. Use [skip-UD-2] in the message
          body to exempt infra-only commits.
```

4. **Make scripts executable**:

```bash
chmod +x scripts/acd-validate.sh scripts/acd-validate-msg.sh
```

5. **Install the hooks** (requires `pre-commit` to be installed):

```bash
pre-commit install
pre-commit install --hook-type commit-msg
```

Report to the human which files were created and the install commands to run. If `pre-commit` is not installed, suggest: `pip install pre-commit` or `brew install pre-commit`.

### When the AI CLI changes

If the project already has the scripts but the human switches to a different AI CLI:

1. Update `ACD_AI_BIN` default and the `run_ai()` function body in both `scripts/acd-validate.sh` and `scripts/acd-validate-msg.sh`.
2. Use the invocation pattern table above to get the correct flags for the new CLI.
3. Run a test commit to verify the hooks still produce `ACD-VALIDATION: PASS / FAIL` correctly.

### When NOT to install

If the project already has the scripts (`scripts/acd-validate.sh`) but hooks are NOT installed in `.git/hooks/`, remind the human to run:

```bash
pre-commit install
pre-commit install --hook-type commit-msg
```

## Instructions

### Step 0: Collect staged changes

Run the following to understand what is staged:

```bash
git diff --cached --name-only          # list of staged files
git diff --cached --stat               # summary of changes
git diff --cached                      # full diff for content inspection
```

Classify staged files into:
- **Production files**: source code files (`.ts`, `.py`, `.go`, etc.)
- **Test files**: files in `__tests__/`, `tests/`, `*.spec.*`, `*.test.*`, `*_test.*`
- **Feature files**: `docs/features/**/*.feature`
- **Spec files**: `docs/tdrs/**/*.md`, `docs/adrs/**/*.md`, `docs/business/**/*.md`

### Step 1: Artifact Consistency checks

**AC-1 — Feature file present**
For every production file staged, at least one `.feature` file must also be staged OR an existing `.feature` file must reference a scenario that covers the changed behavior.

Violation: `[AC-1] Production file <path> has no corresponding feature scenario staged or on disk.`

**AC-2 — @constraints block complete**
For every staged `.feature` file, the `@constraints` block must exist and `governed_by` must list at least one document.

Violation: `[AC-2] <feature-file>: @constraints block missing or governed_by is empty.`

**AC-3 — governed_by documents exist**
Every file path listed under `governed_by` in any staged `.feature` file must exist in the repository.

Violation: `[AC-3] <feature-file>: governed_by references <path> which does not exist.`

**AC-4 — Scenario status updated**
Every scenario that maps to a staged production file must have `@status:implemented` and `@changed:YYYY-MM-DD` in the staged `.feature` file.

Violation: `[AC-4] Scenario "<name>" in <feature-file> is not marked @status:implemented.`

### Step 2: Unified Delivery checks

**UD-1 — Tests staged alongside production code**
If production files are staged, at least one test file must also be staged. A commit with only production code and no tests violates Unified Delivery.

Violation: `[UD-1] Production files staged with no corresponding test files.`

**UD-2 — Commit message format**
Read the commit message from `git log -1 --format="%s%n%b"` (if already committed) or from the `COMMIT_EDITMSG` file for pre-commit context (`cat .git/COMMIT_EDITMSG`).

The message must contain:
- `ACD-session:` line
- `Artifacts:` line
- `Scenarios:` line

Violation: `[UD-2] Commit message missing ACD fields: <list of missing fields>.`

**UD-3 — No direct push to protected branch**
Check the current branch name. If it is `main`, `master`, or matches a protected branch pattern, warn:

Warning: `[UD-3] WARNING: Committing directly to <branch>. ACD requires changes to go through a PR.`

This is a warning, not a blocking violation — the commit is still allowed (the branch protection at the remote level is the real gate).

### Step 3: Traceability checks

**TR-1 — No orphan production code**
For each staged production file, verify there is at least one scenario in a `.feature` file (staged or on disk) that can be semantically linked to it. Use the file path and module name as heuristics (e.g., `src/auth/oauth.ts` → look for a `.feature` file with `auth` or `oauth` in the path or scenarios).

If no link can be inferred, flag it:

Violation: `[TR-1] <production-file>: no traceable scenario found. Either stage the corresponding .feature update or link it manually.`

**TR-2 — No WIP-ACD commits in PR scope**
Check if any staged commit message (or the current message) contains `[WIP-ACD]`. If so, warn:

Warning: `[TR-2] WARNING: WIP-ACD commit detected. Do not open a PR until the session is complete.`

### Step 4: Expert validation (optional, dynamic)

Before producing the final report, discover and invoke any installed `*-acd-expert` skills:

1. **Discover**: Check the list of available skills for any whose name matches the pattern `*-acd-expert` (e.g. `security-acd-expert`, `resilience-acd-expert`, `observability-acd-expert`).
2. **If none found**: skip this step silently. Expert validation is optional — absence of experts does not affect the base validation result.
3. **If one or more found**: invoke each one in turn, passing the staged diff as context. Each expert skill must return a structured result following the **Expert Skill Interface** defined at the end of this document.
4. **Collect results**: gather each expert's `EX-<domain>` verdict (PASS / FAIL / WARN) and include them in the report under the "Expert Validation" section.

Expert FAILs block the commit on the same basis as base checks. Expert WARNs do not block.

To skip all expert validation for a commit, add `[skip-experts]` to the commit message body with a justification.

### Step 5: Produce validation report

Output a structured report:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ACD Commit Validator
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Staged files: <count> production, <count> test, <count> feature, <count> spec

Artifact Consistency
  AC-1 Feature coverage     [PASS|FAIL] <detail>
  AC-2 @constraints block   [PASS|FAIL] <detail>
  AC-3 governed_by exists   [PASS|FAIL] <detail>
  AC-4 Scenario status      [PASS|FAIL] <detail>

Unified Delivery
  UD-1 Tests present        [PASS|FAIL] <detail>
  UD-2 Commit message       [PASS|FAIL] <detail>
  UD-3 Branch protection    [PASS|WARN]  <detail>

Traceability
  TR-1 Orphan code          [PASS|FAIL] <detail>
  TR-2 WIP-ACD marker       [PASS|WARN]  <detail>

Expert Validation                        ← omit section if no experts installed
  EX-security   [PASS|FAIL|WARN] <detail>
  EX-resilience [PASS|FAIL|WARN] <detail>
  EX-<domain>   [PASS|FAIL|WARN] <detail>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ACD-VALIDATION: PASS   ← exit 0
ACD-VALIDATION: FAIL   ← exit 1 (lists all violations)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Exit `0` if no FAIL violations. Exit `1` if any FAIL violation is present. WARNs do not block the commit.

### Step 6: On failure, guide the fix

For each FAIL violation, output a one-line actionable fix:

```
[AC-2] Fix: add @constraints block to docs/features/auth.feature with governed_by populated.
[UD-1] Fix: stage test files for the production changes, or run the acd-session skill to generate them.
[AC-4] Fix: update Scenario "Login with Google" to @status:implemented @changed:2026-03-13.
```

Do not auto-fix violations. The agent reports; the human (or the acd-session skill) fixes.

## Validation scope

| Check | Blocks commit | Configurable |
|---|---|---|
| AC-1 Feature coverage | Yes | Can be disabled for infra-only commits |
| AC-2 @constraints | Yes | No |
| AC-3 governed_by exists | Yes | No |
| AC-4 Scenario status | Yes | No |
| UD-1 Tests present | Yes | Can be disabled for doc-only commits |
| UD-2 Commit message | Yes | No |
| UD-3 Branch protection | No (warn) | No |
| TR-1 Orphan code | Yes | Can be disabled with `[skip-TR-1]` in commit message |
| TR-2 WIP-ACD marker | No (warn) | No |
| EX-* Expert validation | Yes (if FAIL) | All experts skippable with `[skip-experts]` |

To skip a specific check for a commit, add `[skip-<check-id>]` to the commit message body with a justification. Example: `[skip-AC-1] Infrastructure change with no feature impact`.

---

## Expert Skill Interface

Any skill named `*-acd-expert` is automatically discovered and invoked by this validator. To be compatible, an expert skill must follow this interface:

### Input

The validator invokes the expert skill with the staged diff as context:
- List of staged files (`git diff --cached --name-only`)
- Full staged diff (`git diff --cached`)
- Current branch name

### Output

The expert skill must produce a result block in this exact format:

```
EX-<domain>: [PASS|FAIL|WARN]
Checks: <comma-separated list of constraint areas validated>
Detail: <one-line summary>
Violations:
  - <violation description with file path if applicable>
  - ...
Fixes:
  - <one-line actionable fix per violation>
```

- `EX-<domain>` must match the skill name suffix (e.g. skill `security-acd-expert` → `EX-security`)
- `Violations` and `Fixes` are omitted if result is PASS
- The block must end with a line matching `EX-<domain>: PASS`, `EX-<domain>: FAIL`, or `EX-<domain>: WARN` for the validator to parse it

### Expert Skill SKILL.md requirements

An `*-acd-expert` skill must declare in its `SKILL.md`:

```markdown
## Expert domain
<domain-name>  ← must match skill name suffix

## Global constraints validated
- <description of constraint 1 and which TDR/ADR governs it if any>
- <description of constraint 2>
...

## Scope
Global — applies to every commit regardless of feature or governed_by.
```

The `Global constraints validated` list is what makes this skill self-documenting — the validator can surface it in the report so humans know what each expert checked.

## References

- `cliplin-acd/tdrs/acd-agent-delivery-contract.md`
- `cliplin-acd/tdrs/acd-session-workflow.md`
- `cliplin-acd/tdrs/acd-pipeline-gates.md`
- `cliplin-acd/skills/acd-session/SKILL.md`
