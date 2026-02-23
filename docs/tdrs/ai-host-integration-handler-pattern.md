---
tdr: "1.0"
id: "ai-host-integration-handler-pattern"
title: "AI Host Integration Handler Pattern (One Class per Host)"
summary: "Each integration with an AI host (Cursor, Claude Desktop, etc.) is implemented as a class that fulfills a common protocol; the general entry function delegates to the registered handler for that host, avoiding if/elif branches that grow with every new integration."
---

# rules

## Pattern goal (MUST)

- Avoid the function that creates per-AI-tool configuration (e.g. create_ai_tool_config) accumulating many if/elif branches per host.
- One responsibility per host: each integration (Cursor, Claude Desktop, future hosts) is implemented in its own class that knows paths, files, and content specific to that host.
- The entry function (create_ai_tool_config) only: (1) resolves the handler for the ai_tool from a registry, (2) calls a single method on the handler (e.g. apply(target_dir)). It must not contain conditional logic by host name.

## Handler contract (protocol)

- Define a Protocol (typing.Protocol) or ABC with at least:
  - Host identifier (id: str, e.g. "cursor", "claude-desktop").
  - Rules directory path (rules_dir: str) and, if applicable, MCP config file path for validation (mcp_config_path: str | None).
  - Method apply(target_dir: Path) -> None that runs all actions for that host: create directories, write MCP config, write rule files, and any extra files (e.g. instructions.md for Claude Desktop).
- Each concrete implementation of the protocol encapsulates: MCP config creation, rule file paths, and writing each file using shared content (getters in templates or the same module) as appropriate for that host.

## Integration registry (MUST)

- Maintain a registry (dict or map) of ai_tool id -> handler instance. The create_ai_tool_config function obtains the handler by id and calls apply(target_dir).
- Expose: (1) list of known ids (for init/validate and error messages), (2) get handler by id (for create_ai_tool_config and, if needed, for validate). Do not expose concrete implementations to commands; commands depend on the protocol and the registry.

## Where the code lives

- Protocol and registry: in a dedicated module (e.g. src/cliplin/utils/ai_host_integrations/ with base.py or __init__.py that exports the protocol and the registry).
- One class per file or per host in the same package (e.g. cursor.py, claude_desktop.py) that implement the protocol.
- Reusable rule content (long strings for context.mdc, feature-processing, etc.) may remain in templates.py; handlers import and use those getters to avoid duplicating text. The MCP command (command/args) must be the same for all hosts; document in ai-host-integration.ts4 and apply in each handler's create_mcp_config.

## Adding a new host (MUST)

- Create a new class that implements the handler protocol (same contract: id, rules_dir, mcp_config_path if applicable, apply(target_dir)).
- Register the instance in the integration map (one line in the registry module or in __init__.py).
- Optional: add a host-specific TS4 in docs/tdrs/<host>-integration.md and reference it in docs/tdrs/ai-host-integration.md.
- Do not change create_ai_tool_config logic beyond ensuring the new id is in the registry; all logic for the new host stays inside its class.

## Consistency across hosts (MUST)

- The MCP command (uv run cliplin mcp) and shared rules (context, feature-processing, context-protocol-loading, feature-first-flow) must stay aligned across hosts. When changing the MCP command or shared rule content, update all handlers that use it and comply with docs/tdrs/ai-host-integration.md (same command/args, update both generators or all handlers).

## Validation and init

- validate may use the registry to: (1) know if ai_tool is known, (2) get mcp_config_path from the handler to check that the MCP file exists. init uses the list of known ids for the "Unknown AI tool" error message and calls create_ai_tool_config, which already delegates to the handler.
code_refs:
  - "src/cliplin/utils/ai_host_integrations/"
  - "src/cliplin/utils/templates.py"
  - "docs/tdrs/ai-host-integration.md"
  - "docs/tdrs/low-coupling-protocols.md"
  - "docs/tdrs/cursor-integration.md"
  - "docs/tdrs/claude-desktop-integration.md"
