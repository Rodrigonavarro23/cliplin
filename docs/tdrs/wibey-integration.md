---
tdr: "1.0"
id: "wibey-integration"
title: "Wibey AI Integration"
summary: "Rules for configuring Wibey as an AI host for Cliplin (cliplin init --ai wibey). Wibey uses .wibey/ for its folder, .wibey/mcp.json for MCP config, .wibey/rules/ for individual rule files, .wibey/instructions.md for full inline rule content, AGENTS.md at project root as a minimal structured pointer (<2000 chars) that lists the files to load, and .wibey/skills/ for framework skills."
---

# rules

## Host identifier and files

- The AI host identifier for Wibey MUST be `wibey`. This is the value accepted by `cliplin init --ai` and stored in `cliplin.yaml` under the `ai_tool` key.
- Wibey project configuration for this host MUST live in `.wibey/mcp.json` (inside the `.wibey/` directory, not at the project root).
- The rule files for this host MUST be written under `.wibey/rules/` as standard `.md` files (source-of-truth for each individual rule set).
- The full inline Cliplin rule content MUST live in `.wibey/instructions.md`. This file contains all four rule sets (context indexing, feature-first flow, feature processing, context loading protocol) and is the equivalent of `.claude/instructions.md` in the Claude Code integration.
- The primary session bootstrap file is `AGENTS.md` at the project root. Wibey auto-loads `AGENTS.md` at session start by convention.
  - `AGENTS.md` is a **multi-host broader convention** (shared with other tooling such as OpenAI Codex/Agents). Cliplin MUST treat it as a shared file and never overwrite content written by other tools.
  - The Cliplin section in `AGENTS.md` MUST be a **minimal structured pointer** — a list of explicit file paths that Wibey resolves to load the actual rules. It MUST NOT embed full rule content.
  - The Cliplin section in `AGENTS.md` MUST remain **under 2000 characters**. This is a hard constraint: Wibey cannot load files whose size exceeds this limit at session start.
- The AI host integration handler MUST expose:
  - `id = "wibey"`
  - `rules_dir = ".wibey/rules"` (rule files live here as source of truth)
  - `mcp_config_path = ".wibey/mcp.json"` so `cliplin validate` can check that the MCP config exists.

## MCP server configuration for Cliplin context

- `cliplin init --ai wibey` MUST ensure that `.wibey/mcp.json` contains an entry under `mcpServers.cliplin-context` in the standard format:
  - `command` MUST be `"uv"`.
  - `args` MUST be `["run", "cliplin", "mcp"]`.
  - This keeps the effective MCP startup command (`uv run cliplin mcp`) consistent with other hosts — see `ai-host-integration` TDR.
- When `.wibey/mcp.json` already exists, `cliplin init --ai wibey` MUST:
  - Parse the existing file and preserve all settings unrelated to Cliplin.
  - Create or update the `mcpServers` object, adding or overwriting only the `cliplin-context` entry.
  - Never remove other MCP servers defined by the user.
- When `.wibey/mcp.json` does not exist, `cliplin init --ai wibey` MUST:
  - Create the `.wibey/` directory if it does not exist.
  - Create a minimal `.wibey/mcp.json` containing a `mcpServers` object with the `cliplin-context` entry configured as above.

## Context/rules file configuration (instructions.md + AGENTS.md)

### .wibey/instructions.md (full content)

- `cliplin init --ai wibey` MUST create `.wibey/instructions.md` with the same four core rule sets used by other hosts:
  - Context indexing and collection mapping rules.
  - Feature-first flow rules.
  - Feature processing rules.
  - Context loading protocol rules.
- Content MUST be generated from shared template functions in `templates.py` (do not duplicate content by hand).
- This file is the Wibey equivalent of `.claude/instructions.md`. It holds the full rule content that would be too large for `AGENTS.md`.

### AGENTS.md (minimal structured pointer)

- `cliplin init --ai wibey` MUST create or update `AGENTS.md` at the project root.
- The Cliplin section written to `AGENTS.md` MUST be a **direct imperative session-start instruction** — not embedded rule content. It must command the agent to load the files before any interaction and mention that files with `alwaysApply: true` apply automatically every session. Format:

  ```
  <!-- cliplin-wibey-start -->
  # Cliplin — Session Start (always execute)

  At the start of every new session, before any other interaction, you MUST load the following files.
  Files that include the rule `alwaysApply: true` must be applied automatically in every session:

  - .wibey/instructions.md
  - .wibey/rules/context.md
  - .wibey/rules/feature-first-flow.md
  - .wibey/rules/feature-processing.md
  - .wibey/rules/context-protocol-loading.md

  This is a mandatory session-start instruction. Execute it without exception before responding to any request.
  <!-- cliplin-wibey-end -->
  ```

- The Cliplin section MUST remain **under 2000 characters** (hard constraint — Wibey cannot load files exceeding this limit at session start).
- Because `AGENTS.md` is a multi-host shared file, Cliplin MUST use a merge strategy:
  - If `AGENTS.md` does not exist, create it with the minimal pointer content.
  - If `AGENTS.md` already exists, locate the Cliplin section via `<!-- cliplin-wibey-start -->` / `<!-- cliplin-wibey-end -->` markers and replace only that section.
  - If no markers are found, append the pointer content.
  - Cliplin MUST NOT remove any existing sections written by other tools.
- Rule files under `.wibey/rules/` serve as the structured source of truth for each rule set. They are created with the same content as `.claude/rules/` (standard `.md` extension, not `.mdc`).

## Init behaviour and id registry

- The AI host integration for Wibey MUST be implemented as a class that follows the shared `AiHostIntegration` protocol (see `ai-host-integration-handler-pattern` TDR):
  - The class lives under `src/cliplin/utils/ai_host_integrations/wibey.py`.
  - It implements `apply(target_dir: Path) -> None`, which: creates `.wibey/` directory, creates `.wibey/rules/*.md`, creates `.wibey/instructions.md`, creates/updates `.wibey/mcp.json`, creates/updates `AGENTS.md` (minimal pointer), and links framework skills.
- The integration MUST be registered in the central registry so that:
  - `get_known_ai_tool_ids()` includes `"wibey"` alongside `"cursor"`, `"claude-code"`, `"gemini"`, and `"opencode"`.
  - `create_ai_tool_config(project_root, "wibey")` delegates to the Wibey integration handler.
- `cliplin init --ai wibey` MUST:
  - Validate that `"wibey"` is a known AI tool id via the registry.
  - Call the integration handler to perform all Wibey-specific configuration steps.
  - Keep the rest of the initialization flow identical to other hosts (directory structure, framework package, ChromaDB initialization, validation, and framework reindex).

## Validation behaviour

- `cliplin validate` MUST treat the Wibey integration like other hosts:
  - When `cliplin.yaml` has `ai_tool: wibey`, `validate` MUST use the integration registry to obtain `mcp_config_path` and check that `.wibey/mcp.json` exists.
  - Missing `.wibey/mcp.json` MUST be reported as an error: "Missing MCP config file for ai_tool 'wibey': .wibey/mcp.json".
- The validation logic MUST remain host-agnostic: it uses `get_integration(ai_tool)` and reads `mcp_config_path`; it does not special-case `"wibey"` by name.

## Skills support (MUST)

- `cliplin init --ai wibey` MUST link framework skills after `create_framework_knowledge_package` completes.
- The `WibeyIntegration` handler MUST call `link_knowledge_skills(project_root, framework_base)` in its `apply()` method, so the built-in audit skill appears at `.wibey/skills/<skill-name>/SKILL.md`.
- `framework_base` is `target_dir / ".cliplin" / "knowledge" / FRAMEWORK_PACKAGE_DIR`.
- The `.wibey/skills/` directory and its contents are created as hard links, consistent with how Claude Code handles skill linking.
- Re-running `cliplin init --ai wibey` MUST refresh the link (existing link is removed and recreated), because `link_knowledge_skills` already handles this via `shutil.rmtree` on the destination before re-linking.
- If the hard-link creation fails at init time (e.g. `OSError`, cross-filesystem): **warn and continue** — init MUST NOT fail because of a skill link failure. Log a warning to stderr and proceed.

## Wibey vs Claude Code structural comparison

| Aspect | Claude Code | Wibey |
|--------|-------------|-------|
| Host folder | `.claude/` | `.wibey/` |
| MCP config | `.mcp.json` (project root) | `.wibey/mcp.json` |
| Rules folder | `.claude/rules/` | `.wibey/rules/` |
| Rule file ext | `.md` | `.md` |
| Full rule content file | `.claude/instructions.md` | `.wibey/instructions.md` |
| Session bootstrap file | `.claude/claude.md` (README) | `AGENTS.md` (project root, multi-host convention) |
| Auto-load mechanism | Loaded via CLAUDE.md / instructions | Wibey reads `AGENTS.md` at session start |
| AGENTS.md / bootstrap content | N/A | Minimal structured pointer (<2000 chars) listing files to load |
| Skills folder | `.claude/skills/` | `.wibey/skills/` |

code_refs:
  - "docs/features/cli.feature"
  - "docs/tdrs/ai-host-integration.md"
  - "docs/tdrs/ai-host-integration-handler-pattern.md"
  - "src/cliplin/utils/ai_host_integrations/wibey.py"
  - "src/cliplin/utils/templates.py"
