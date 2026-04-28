---
tdr: "1.0"
id: "opencode-integration"
title: "OpenCode AI Integration"
summary: "Rules for configuring OpenCode AI as an AI host for Cliplin (cliplin init --ai opencode)."
---

# rules

## Host identifier and files

- The AI host identifier for OpenCode MUST be `opencode`. This is the value accepted by `cliplin init --ai` and stored in `cliplin.yaml` under the `ai_tool` key.
- OpenCode project configuration for this host MUST live in `opencode.json` at the project root. This is the standard OpenCode project config file (supports JSON and JSONC).
- The primary instructional context file for this host MUST be `OPENCODE.md` at the project root. It is referenced via the `instructions` array in `opencode.json`.
- The AI host integration handler MUST expose:
  - `id = "opencode"`
  - `rules_dir = "."` (rules live in `OPENCODE.md` at project root)
  - `mcp_config_path = "opencode.json"` so `cliplin validate` can check that the OpenCode config file exists.

## MCP server configuration for Cliplin context

- `cliplin init --ai opencode` MUST ensure that `opencode.json` contains an entry under `mcp.cliplin-context` compatible with the OpenCode local MCP server format:
  - `type` MUST be `"local"`.
  - `command` MUST be `["uv", "run", "cliplin", "mcp"]` (an array containing the executable and arguments).
  - This keeps the effective MCP startup command (`uv run cliplin mcp`) consistent with other hosts even though OpenCode uses a different JSON shape (array vs separate command/args fields) — see `ai-host-integration` TDR.
- When `opencode.json` already exists, `cliplin init --ai opencode` MUST:
  - Parse the existing file and preserve all settings unrelated to Cliplin.
  - Create or update the `mcp` object, adding or overwriting only the `cliplin-context` entry.
  - Never remove other MCP servers defined by the user.
- When `opencode.json` does not exist, `cliplin init --ai opencode` MUST:
  - Create a minimal `opencode.json` at the project root containing at least:
    - A `mcp` object with the `cliplin-context` entry configured as above.
    - An `instructions` array containing `"OPENCODE.md"`.

## Context/rules file configuration (OPENCODE.md)

- `cliplin init --ai opencode` MUST create or update an `OPENCODE.md` file at the project root with Cliplin project rules and conventions, loaded by OpenCode via the `instructions` setting.
- The content of `OPENCODE.md` MUST:
  - Include the same core rule sets used by other hosts:
    - Context indexing and collection mapping rules.
    - Feature-first flow rules.
    - Feature processing rules.
    - Context loading protocol rules.
  - Be generated from shared template functions in `templates.py` (do not duplicate content by hand).
- `opencode.json` MUST be configured so that `OPENCODE.md` is loaded as an instruction file:
  - If the `instructions` key is missing, `cliplin init --ai opencode` MUST add `"instructions": ["OPENCODE.md"]`.
  - If `instructions` already exists as an array, Cliplin MUST ensure `"OPENCODE.md"` is present without removing existing entries.
  - Cliplin MUST NOT remove any existing `instructions` entries.

## Init behaviour and id registry

- The AI host integration for OpenCode MUST be implemented as a class that follows the shared `AiHostIntegration` protocol (see `ai-host-integration-handler-pattern` TDR):
  - The class lives under `src/cliplin/utils/ai_host_integrations/opencode.py`.
  - It implements `apply(target_dir: Path) -> None`, which creates/updates `opencode.json` and `OPENCODE.md`.
- The integration MUST be registered in the central registry so that:
  - `get_known_ai_tool_ids()` includes `"opencode"` alongside `"cursor"`, `"claude-code"`, and `"gemini"`.
  - `create_ai_tool_config(project_root, "opencode")` delegates to the OpenCode integration handler.
- `cliplin init --ai opencode` MUST:
  - Validate that `"opencode"` is a known AI tool id via the registry.
  - Call the integration handler to perform all OpenCode-specific configuration steps.
  - Keep the rest of the initialization flow identical to other hosts (directory structure, framework package, ChromaDB initialization, validation, and framework reindex).

## Validation behaviour

- `cliplin validate` MUST treat the OpenCode integration like other hosts:
  - When `cliplin.yaml` has `ai_tool: opencode`, `validate` MUST use the integration registry to obtain `mcp_config_path` and check that `opencode.json` exists.
  - Missing `opencode.json` MUST be reported as an error: "Missing MCP config file for ai_tool 'opencode': opencode.json".
- The validation logic MUST remain host-agnostic: it uses `get_integration(ai_tool)` and reads `mcp_config_path`; it does not special-case `"opencode"` by name.

## Skills support for OpenCode (MUST)

- `cliplin init --ai opencode` MUST link framework skills after `create_framework_knowledge_package` completes.
- The `OpenCodeIntegration` handler MUST call `link_knowledge_skills(project_root, framework_base)` in its `apply()` method, so the built-in audit skill appears at `.opencode/skills/<skill-name>/SKILL.md`.
- `framework_base` is `target_dir / ".cliplin" / "knowledge" / FRAMEWORK_PACKAGE_DIR`.
- The `.opencode/skills/` directory and its contents are created as hard links, consistent with how other hosts handle skill linking.
- Re-running `cliplin init --ai opencode` MUST refresh the link (existing link is removed and recreated), because `link_knowledge_skills` already handles this via `shutil.rmtree` on the destination before re-linking.
- If the hard-link creation fails at init time (e.g. `OSError`, cross-filesystem): **warn and continue** — init MUST NOT fail because of a skill link failure. Log a warning to stderr and proceed.

## OpenCode MCP config format vs other hosts

- OpenCode uses `"type": "local"` and `"command": [...]` (array) — this differs from Cursor/Claude which use `"command": "uv"` + `"args": [...]` (separate fields). This is a host-specific quirk in the JSON shape; the effective startup command (`uv run cliplin mcp`) remains consistent across all hosts per the `ai-host-integration` TDR.
- The `OpenCodeIntegration` handler MUST NOT reuse `create_cursor_mcp_config` or `create_claude_desktop_mcp_config` from `templates.py` for the MCP config — it MUST write the `opencode.json` format directly.

## Consistency with OpenCode configuration model

- The structure of `opencode.json` MUST respect the OpenCode configuration model (https://opencode.ai/docs/config):
  - MCP servers are defined under the top-level `mcp` object.
  - Instructions are loaded via the top-level `instructions` array (accepts paths and glob patterns).
- Cliplin MUST avoid writing to user- or system-level OpenCode configuration files:
  - It MUST NOT touch `~/.config/opencode/opencode.json` or system settings.
  - It only creates or updates `opencode.json` in the project root.

code_refs:
  - "docs/features/cli.feature"
  - "docs/tdrs/ai-host-integration.md"
  - "docs/tdrs/ai-host-integration-handler-pattern.md"
  - "src/cliplin/utils/ai_host_integrations/opencode.py"
  - "src/cliplin/utils/templates.py"
