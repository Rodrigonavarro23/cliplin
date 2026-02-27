---
tdr: "1.0"
id: "gemini-integration"
title: "Gemini CLI Integration"
summary: "Rules for configuring Gemini CLI as an AI host for Cliplin (cliplin init --ai gemini)."
---

# rules

## Host identifier and files

- The AI host identifier for Gemini CLI MUST be `gemini`. This is the value accepted by `cliplin init --ai` and stored in `cliplin.yaml` under the `ai_tool` key.
- Gemini CLI project configuration for this host MUST live in `.gemini/settings.json` at the project root. This file is the project settings file described in the Gemini CLI configuration docs (`settings.json` inside the `.gemini` directory).
- The primary instructional context file for this host MUST be `GEMINI.md` at the project root, loaded as hierarchical context by Gemini CLI (see `context.fileName` in `.gemini/settings.json`).
- The AI host integration handler MUST expose:
  - `id = "gemini"`
  - `rules_dir = "."` (rules live in `GEMINI.md` at project root)
  - `mcp_config_path = ".gemini/settings.json"` so `cliplin validate` can check that the Gemini settings file exists.

## MCP server configuration for Cliplin context

- `cliplin init --ai gemini` MUST ensure that `.gemini/settings.json` contains a `mcpServers.cliplin-context` entry compatible with other hosts:
  - `command` MUST be `"uv"`.
  - `args` MUST be `["run", "cliplin", "mcp"]`.
  - This keeps the MCP startup command consistent across Cursor, Claude Desktop, and Gemini CLI (see `ai-host-integration` TDR).
- When `.gemini/settings.json` already exists, `cliplin init --ai gemini` MUST:
  - Preserve existing settings unrelated to Cliplin (do not discard user configuration).
  - Create or update the `mcpServers` object, adding or overwriting only the `cliplin-context` entry.
  - Never remove other MCP servers defined by the user.
- When `.gemini/settings.json` does not exist, `cliplin init --ai gemini` MUST:
  - Create the `.gemini/` directory if missing.
  - Create a minimal `settings.json` containing at least:
    - A `mcpServers` object with the `cliplin-context` entry configured as above.

## Context file configuration (GEMINI.md)

- `cliplin init --ai gemini` MUST create or update a `GEMINI.md` file at the project root with Cliplin project rules and conventions, so Gemini CLI can load it as hierarchical context.
- The content of `GEMINI.md` MUST:
  - Include the same core rule sets used by other hosts:
    - Context indexing and collection mapping rules (context.mdc).
    - Feature-first flow rules (feature-first-flow).
    - Feature processing rules (feature-processing).
    - Context loading protocol rules (context-protocol-loading).
  - Be generated from shared template functions in `templates.py` (do not duplicate content by hand).
- `.gemini/settings.json` MUST be configured so that `GEMINI.md` is loaded as a context file:
  - If the `context` section is missing, `cliplin init --ai gemini` SHOULD add:
    - `context.fileName: ["GEMINI.md"]`
  - If `context.fileName` already exists:
    - If it is a string, Cliplin SHOULD keep the existing value and, if different from `"GEMINI.md"`, convert it to an array that also includes `"GEMINI.md"`.
    - If it is an array, Cliplin SHOULD ensure `"GEMINI.md"` is present without removing existing entries.
  - Cliplin MUST NOT remove any existing context-related settings other than augmenting `fileName` to include `GEMINI.md`.

## Init behaviour and id registry

- The AI host integration for Gemini CLI MUST be implemented as a class that follows the shared `AiHostIntegration` protocol (see `ai-host-integration-handler-pattern` TDR):
  - The class lives under `src/cliplin/utils/ai_host_integrations/` (for example `gemini_cli.py`).
  - It implements `apply(target_dir: Path) -> None`, which creates/updates `.gemini/settings.json` and `GEMINI.md`.
- The integration MUST be registered in the central registry so that:
  - `get_known_ai_tool_ids()` includes `"gemini"` alongside `"cursor"` and `"claude-desktop"`.
  - `create_ai_tool_config(project_root, "gemini")` delegates to the Gemini integration handler.
- `cliplin init --ai gemini` MUST:
  - Validate that `"gemini"` is a known AI tool id via the registry.
  - Call the integration handler to perform all Gemini-specific configuration steps.
  - Keep the rest of the initialization flow identical to other hosts (directory structure, framework package, ChromaDB initialization, validation, and framework reindex).

## Validation behaviour

- `cliplin validate` MUST treat the Gemini integration like other hosts:
  - When `cliplin.yaml` has `ai_tool: gemini`, `validate` MUST use the integration registry to obtain `mcp_config_path` and check that `.gemini/settings.json` exists.
  - Missing `.gemini/settings.json` MUST be reported as an error: "Missing MCP config file for ai_tool 'gemini': .gemini/settings.json".
- The validation logic MUST remain host-agnostic: it uses `get_integration(ai_tool)` and reads `mcp_config_path`; it does not special-case `"gemini"` by name.

## Consistency with Gemini CLI configuration model

- The structure of `.gemini/settings.json` MUST respect the Gemini CLI configuration model ([Gemini CLI configuration](https://geminicli.com/docs/reference/configuration/)):
  - The Cliplin integration writes into the top-level `mcpServers` object for MCP server definitions.
  - Project-specific instructional context is provided through `GEMINI.md` (and referenced via `context.fileName`), not by overloading unrelated settings.
- Cliplin MUST avoid writing to user- or system-level Gemini CLI configuration files:
  - It MUST NOT touch `~/.gemini/settings.json` or system settings.
  - It only creates or updates `.gemini/settings.json` in the project root.

code_refs:
  - "docs/features/cli.feature"
  - "docs/tdrs/ai-host-integration.md"
  - "docs/tdrs/ai-host-integration-handler-pattern.md"
  - "src/cliplin/utils/ai_host_integrations/gemini_cli.py"
  - "src/cliplin/utils/templates.py"

