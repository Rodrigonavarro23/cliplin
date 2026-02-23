---
tdr: "1.0"
id: "knowledge-reindex-context"
title: "Context Store and Reindex for Knowledge Packages"
summary: "Include .cliplin/knowledge/** in context locations; map package content to the same collections as project docs; reindex and fingerprint store behavior on add/update/remove."
---

# rules

## Context locations — include knowledge packages (MUST)

- The single source of truth for context directories (see docs/tdrs/system-modules.md) MUST include `.cliplin/knowledge/**` as additional roots to scan
- Under each package root (e.g. `.cliplin/knowledge/commons-.../`), apply the same type-to-collection mapping as for project docs: e.g. paths containing segment `adrs` or `docs/adrs` and extension `.md` → business-and-architecture; `docs/tdrs` or `tdrs` + `.md` → technical-decision-records; `.ts4` files → tech-specs; `.feature` → features; business-like paths + `.md` → business-and-architecture; ui-intent-like paths + `.yaml` → uisi. Exact segment names and patterns MUST be defined in one place (e.g. COLLECTION_MAPPINGS or KNOWLEDGE_PATH_MAPPINGS in utils/chromadb.py) so that both project docs and knowledge package docs use the same rules
- Structure-agnostic: scan recursively under each package; any file matching the type rules (e.g. any .md under an adr path, any .ts4 anywhere under the package) MUST be indexed into the corresponding collection, regardless of extra subfolders (e.g. docs/adrs/framework/001-foo.md and docs/adrs/002-bar.md both map to business-and-architecture)

## Document ID and metadata (MUST)

- Document ID MUST be a stable path relative to project root (e.g. `.cliplin/knowledge/commons-.../docs/adrs/001-foo.md`) so that the same file is upserted on reindex and can be deleted when the package is removed
- Metadata MUST include at least file_path, type, collection; MAY include a package identifier (e.g. knowledge package name) for filtering

## Reindex after add/update (MUST)

- After `cliplin knowledge add` or `cliplin knowledge update`, the implementation MUST trigger reindex for the affected package (all files under that package root that match context type rules). Use the same reindex logic and fingerprint store as the main reindex command so that incremental behavior and "list changed" stay correct
- After successful index of each file, update the fingerprint store per ADR-002 / ADR-003

## Remove package — purge from context (MUST)

- When `cliplin knowledge remove` runs, the implementation MUST delete from the context store all documents whose file_path is under the removed package root (e.g. all IDs starting with `.cliplin/knowledge/commons-.../`). MUST also remove or update fingerprint store entries for those paths so that "list changed documents" and future reindex do not treat them as current

## Skills (host-specific, optional)

- If the host integration supports skills (e.g. Claude Desktop), skills from an installed knowledge package MAY be exposed via hard links (or equivalent) under the host’s skills directory (e.g. `.claude/skills`) so the host sees them as installed. On `knowledge remove`, those links MUST be removed. If the host does not support skills or the integration does not implement this, no action is taken for skills; see docs/tdrs/claude-desktop-integration.md for Claude-specific behavior
code_refs:
  - "src/cliplin/commands/reindex.py"
  - "src/cliplin/commands/knowledge.py"
  - "src/cliplin/utils/chromadb.py"
  - "docs/tdrs/system-modules.md"
  - "docs/tdrs/knowledge-packages.md"
  - "docs/tdrs/claude-desktop-integration.md"
  - "docs/adrs/002-chromadb-rag-context-base.md"
  - "docs/adrs/003-incremental-context-reindexing.md"
  - "docs/adrs/005-knowledge-packages.md"
  - "docs/features/knowledge.feature"
