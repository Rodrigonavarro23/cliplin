# ADR-004: MCP Server Must Expose Instructions

## Status
Accepted

## Context

The Cliplin MCP server (context store) is started by hosts such as Cursor or Claude Desktop via a config file (e.g. `.cursor/mcp.json`). The host performs an MCP handshake (`initialize`) and may send a **GetInstructions** action to obtain a short description of the server's purpose and how to use it.

If the server does not expose **instructions** (or equivalent server info), some hosts:

- Send GetInstructions and receive no usable response
- Log **"No server info found"** and treat the server as misconfigured or broken
- May not surface the server correctly in the UI or may show errors to the user

This occurred with the Cliplin MCP server when it was built with FastMCP using only `name` and `json_response=True`, without the `instructions` parameter. Cursor reported "No server info found" until instructions were added.

## Decision

**The Cliplin MCP server MUST expose server instructions** so that the host receives both `serverInfo` and `instructions` in the MCP `initialize` response (and in response to GetInstructions if the host sends it).

- When using **FastMCP**: construct the server with the `instructions` parameter set to a non-empty string. The string should describe what the server does and how to use it (e.g. which tools to call, which collections exist, and the rule "never proceed without loading context").
- When using another MCP implementation: ensure the server returns equivalent metadata (name, version, and a short instruction text) in the handshake so that hosts do not log "No server info found" or treat the server as misconfigured.

Technical rules are prescribed in the TS4 (e.g. "MCP server must expose instructions (MUST)" in system-modules).

## Consequences

### Positive

- Hosts (Cursor, Claude Desktop, etc.) receive server info and instructions; no "No server info found" errors.
- Users and AI agents see a clear description of how to use the context server (which tools, which collections).
- Compliance with host expectations improves integration and reduces support burden.

### Negative

- Instructions must be kept in sync with the actual tools and collections; if they drift, the instructions become misleading. Mitigation: keep instructions short and generic (e.g. "Use chroma_query_documents; collections: …") and update them when adding or renaming collections or changing usage rules.

## Lesson learned

**Symptom**: Cursor logs "No server info found" when connecting to the Cliplin MCP server.  
**Cause**: The MCP server was not exposing `instructions` in the initialize response (FastMCP was created without the `instructions` parameter).  
**Fix**: Add `instructions=<short description>` to the FastMCP constructor so the server returns both serverInfo and instructions.  
**Prevention**: Document in TS4 and ADR that any Cliplin MCP server MUST expose instructions for host compatibility.

## References

- TS4: system-modules — "MCP server must expose instructions (MUST)"
- docs/business/framework.md — Section 9 (Context Access via MCP)
