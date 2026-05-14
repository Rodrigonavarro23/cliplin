---
tdr: "1.0"
id: "wibey-integration"
title: "Wibey AI Integration"
summary: "Rules for configuring Wibey as an AI host for Cliplin (cliplin init --ai wibey). Wibey uses .wibey/ for its folder, .wibey/mcp.json for MCP config, .wibey/rules/ for rule files, AGENTS.md at project root as the inline instructional context file (multi-host convention), and .wibey/skills/ for framework skills."
---

# rules

## Host identifier and files

- The AI host identifier for Wibey MUST be `wibey`. This is the value accepted by `cliplin init --ai` and stored in `cliplin.yaml` under the `ai_tool` key.
- Wibey project configuration for this host MUST live in `.wibey/mcp.json` (inside the `.wibey/` directory, not at the project root).
- The rule files for this host MUST be written under `.wibey/rules/` as standard `.md` files — Wibey does NOT support a rules subfolder natively; the rule files live there for source-of-truth storage but the instructional entry point is `AGENTS.md`.
- The primary instructional context file for this host MUST be `AGENTS.md` at the project root. Wibey auto-loads `AGENTS.md` at session start by convention.
- `AGENTS.md` is a **multi-host broader convention** (shared with other tooling such as OpenAI Codex/Agents). Cliplin MUST treat it as a shared file and never overwrite content written by other tools.
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

## Context/rules file configuration (AGENTS.md)

- `cliplin init --ai wibey` MUST create or update `AGENTS.md` at the project root with full inline Cliplin rule content so that Wibey auto-loads them at session start.
- The content of `AGENTS.md` MUST include the same core rule sets used by other hosts:
  - Context indexing and collection mapping rules.
  - Feature-first flow rules.
  - Feature processing rules.
  - Context loading protocol rules.
- Content MUST be generated from shared template functions in `templates.py` (do not duplicate content by hand).
- Because `AGENTS.md` is a multi-host shared file, Cliplin MUST use a merge strategy:
  - If `AGENTS.md` does not exist, create it with the Cliplin rule content.
  - If `AGENTS.md` already exists, locate and update only the Cliplin-owned section (identifiable by a Cliplin section header) without removing or overwriting other sections.
  - Cliplin MUST NOT remove any existing sections written by other tools.
- Rule files under `.wibey/rules/` serve as the structured source of truth for each rule set. They are created with the same content as `.claude/rules/` (standard `.md` extension, not `.mdc`).

## Init behaviour and id registry

- The AI host integration for Wibey MUST be implemented as a class that follows the shared `AiHostIntegration` protocol (see `ai-host-integration-handler-pattern` TDR):
  - The class lives under `src/cliplin/utils/ai_host_integrations/wibey.py`.
  - It implements `apply(target_dir: Path) -> None`, which: creates `.wibey/` directory, creates `.wibey/rules/*.md`, creates/updates `.wibey/mcp.json`, creates/updates `AGENTS.md`, and links framework skills.
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
| Instructional file | `.claude/instructions.md` | `AGENTS.md` (project root, shared convention) |
| Auto-load mechanism | Loaded via CLAUDE.md / instructions | Wibey reads `AGENTS.md` at session start |
| Skills folder | `.claude/skills/` | `.wibey/skills/` |
| Inline content strategy | Separate instructions.md | Inline content in AGENTS.md |

code_refs:
  - "docs/features/cli.feature"
  - "docs/tdrs/ai-host-integration.md"
  - "docs/tdrs/ai-host-integration-handler-pattern.md"
  - "src/cliplin/utils/ai_host_integrations/wibey.py"
  - "src/cliplin/utils/templates.py"
