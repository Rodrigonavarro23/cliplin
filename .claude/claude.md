# Claude Desktop Configuration for Cliplin

This directory contains rules and instructions for using Claude Desktop with this Cliplin project. Rules are loaded from `.claude/rules/`.

## Files

- **`.mcp.json`** (at project root): MCP server configuration for Cliplin context access
- **`instructions.md`**: Consolidated instructions file with all project rules (LOAD THIS FIRST)
- **`rules/context.md`**: Context indexing rules and context store collection mappings
- **`rules/feature-first-flow.md`**: Feature-first flow (spec before code); feature file as source of truth
- **`rules/feature-processing.md`**: Feature file processing and implementation rules
- **`rules/context-protocol-loading.md`**: Context loading protocol rules

## How to Load Rules in Claude Desktop

### Option 1: Load Instructions File (Recommended)

At the start of each conversation, copy and paste the contents of `instructions.md` into Claude Desktop. This will load all project rules at once.

### Option 2: Create a Claude Skill (Advanced)

You can create a Claude Skill from the `.claude` directory:

1. Zip the `.claude` directory (MCP config is at project root in `.mcp.json`, not inside `.claude`)
2. In Claude Desktop, go to **Settings > Extensions**
3. Click "Advanced Settings" and find "Extension Developer"
4. Click "Install Extension..." and select the ZIP file
5. Claude will automatically apply these rules in relevant contexts

### Option 3: Reference Individual Rule Files

Reference files under `.claude/rules/` as needed:
- For context loading: reference `rules/context-protocol-loading.md`
- For feature work: reference `rules/feature-processing.md`
- For indexing: reference `rules/context.md`

## MCP Server Configuration

The `.mcp.json` file at the project root configures the Cliplin context MCP server. This allows Claude to:
- Query project context from the context store collections (via Cliplin MCP)
- Access ADRs, features, TS4 specs, and UI Intent files from `docs/` and `.cliplin/knowledge/**` (built-in framework + knowledge packages)
- Load relevant context before starting any task

Make sure the MCP server is properly configured in Claude Desktop's settings to use the project's `.mcp.json`.

## Important Notes

- **Always load context first**: Before any coding, debugging, or implementation task, query the context store collections via the Cliplin MCP server
- **Follow the protocol**: The context loading protocol is mandatory and prevents wasted tokens and misaligned code
- **Update rules**: If you modify any rule files in `.claude/rules/`, reload them in Claude Desktop

For more information about Cliplin, see the main project README.
