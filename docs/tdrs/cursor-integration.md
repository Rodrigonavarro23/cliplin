---
tdr: "1.0"
id: "cursor-integration"
title: "Cursor IDE Integration"
summary: "Cursor-specific config, rules location, and quirks so that Cliplin templates and MCP behavior work correctly in Cursor."
---

# rules

## Config and paths (Cursor-only)

- **MCP config**: `.cursor/mcp.json`; key `mcpServers["cliplin-context"]`
- **Rules**: `.cursor/rules/*.mdc` (always-applied and conditional rules)
- **Template generator**: `create_cursor_mcp_config(target_dir)` in `src/cliplin/utils/templates.py` writes `.cursor/mcp.json`
- Cursor typically uses project root as cwd when mcp.json is in the project; the MCP server runs with that cwd

## Cursor-specific MCP behavior (MUST)

- Cursor may send GetInstructions after initialize; the Cliplin MCP server MUST expose `instructions` in the initialize response so Cursor receives server info (see ADR-004, docs/tdrs/system-modules.md)
- Without instructions, Cursor can log "No server info found" or treat the server as misconfigured

## When changing Cursor-only behavior

- Changes to Cursor rules (e.g. new .mdc in .cursor/rules/) or to the content generated for Cursor must stay consistent with docs/tdrs/ai-host-integration.md for the shared MCP command (same command/args as other hosts)
- If adding Cursor-specific templates (e.g. new rule file), document the path and purpose in this TS4

## Cross-references

- Shared MCP command and multi-host checklist: docs/tdrs/ai-host-integration.md
- MCP server instructions requirement: docs/adrs/004-mcp-server-instructions.md, docs/tdrs/system-modules.md
code_refs:
  - "src/cliplin/utils/templates.py"
  - "docs/tdrs/ai-host-integration.md"
  - "docs/tdrs/system-modules.md"
  - "docs/adrs/004-mcp-server-instructions.md"
  - ".cursor/rules/"
