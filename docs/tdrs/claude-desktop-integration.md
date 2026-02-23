---
tdr: "1.0"
id: "claude-desktop-integration"
title: "Claude Desktop Integration"
summary: "Claude Desktop-specific config, rules, and Skills so that Cliplin templates and MCP behavior work correctly in Claude Desktop."
---

# rules

## Config and paths (Claude Desktop-only)

- **MCP config**: `.mcp.json` at project root (not inside .claude); key `mcpServers["cliplin-context"]`
- **Rules**: `.claude/rules/` — e.g. context.md, feature-first-flow.md, feature-processing.md, context-protocol-loading.md
- **Instructions**: `.claude/instructions.md` (consolidated rules); `.claude/claude.md` (directory README for users)
- **Template generator**: `create_claude_desktop_mcp_config(target_dir)` in `src/cliplin/utils/templates.py` writes `.mcp.json` at project root
- Init also creates `.claude/rules/*.md`, `.claude/instructions.md`, and `.claude/claude.md` when ai_tool is claude-desktop

## Claude Desktop Skills (MUST document, MAY support in templates)

- Claude Desktop supports **Skills** (extensions): a zip of project-specific rules/instructions that users can install via Settings > Extensions > Extension Developer > Install Extension
- For Cliplin, a Skill can be created by zipping the `.claude` directory; the MCP config lives at project root (`.mcp.json`), so the zip contains rules and instructions, not the MCP config (user or project must have .mcp.json at the right place for MCP to work)
- When documenting or generating "how to use with Claude Desktop", mention: (1) load instructions.md at conversation start, (2) optional: create a Skill from the `.claude` directory for automatic rule application
- Any new Claude-specific capability (e.g. Skill packaging, extra rule files) must be documented in this TS4 and kept in sync with what `cliplin init --ai-tool claude-desktop` produces

## Knowledge packages — Skills from .cliplin/knowledge (MUST when supported)

- When a knowledge package is installed via `cliplin knowledge add` and the package contains a skills directory (or host-equivalent), the Claude Desktop integration MAY expose those skills under `.claude/skills` so they appear as installed to Claude Desktop. On `cliplin knowledge remove`, those links MUST be removed. If the integration does not implement this, it performs no action for skills; the rest of the knowledge feature (context store, reindex) still applies. See docs/tdrs/knowledge-reindex-context.md and docs/adrs/005-knowledge-packages.md.
- Skills layout: Claude Desktop expects one level under `.claude/skills/`, e.g. `.claude/skills/<skill_name>/SKILL.md`. The implementation finds all folders under `package_path/skills/` that contain `SKILL.md` and creates hard links for each file directly under `.claude/skills/<folder_name>`, handling both repo layouts: (1) `skills/skill-folder/SKILL.md` -> `.claude/skills/skill-folder/`; (2) `skills/<pkg-repo>/skill-folder/SKILL.md` -> `.claude/skills/skill-folder/` (skips the wrapper level). Uses hard links only (no copy fallback). Do NOT create an extra package-named level as Claude would not recognize multiple nesting levels.

## When changing Claude Desktop-only behavior

- Changes to Claude rules (e.g. new file in .claude/rules/) or to instructions/claude.md content must stay consistent with docs/tdrs/ai-host-integration.md for the shared MCP command (same command/args as other hosts)
- If adding Claude-specific templates (e.g. Skill manifest, new rule), document the path and purpose in this TS4

## Cross-references

- Shared MCP command and multi-host checklist: docs/tdrs/ai-host-integration.md
- MCP server instructions: docs/adrs/004-mcp-server-instructions.md, docs/tdrs/system-modules.md (server must expose instructions for all hosts)
code_refs:
  - "src/cliplin/utils/templates.py"
  - "docs/tdrs/ai-host-integration.md"
  - "docs/tdrs/system-modules.md"
  - "docs/adrs/004-mcp-server-instructions.md"
  - "docs/tdrs/knowledge-reindex-context.md"
  - "docs/adrs/005-knowledge-packages.md"
  - ".claude/"
