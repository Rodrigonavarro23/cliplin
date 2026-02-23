# TDR — Technical Decision Records

## Evolution from TS4 to TDR

**TS4** (Technical Specs for AI) remains **supported but deprecated**. Cliplin now prefers **TDR** (Technical Decision Record), a Markdown-based format that:

- **Improves compatibility** across AI systems (Cursor, Claude, etc.) by using standard Markdown instead of a custom YAML format
- **Keeps the same conceptual model** as TS4: technical rules, code references, and clear structure
- **Lives in** `docs/tdrs/` and is indexed in the `technical-decision-records` collection

If your project still uses `docs/ts4/`, consider migrating to `docs/tdrs/` (TDR). When loading context, prefer querying `technical-decision-records` first; use `tech-specs` (TS4) as fallback or when suggesting migration.

## TDR format definition

A TDR is a **Markdown file** (`.md`) with:

1. **YAML frontmatter** (between `---` lines) with:
   - `tdr`: format version (e.g. `"1.0"`)
   - `id`: kebab-case identifier (e.g. `"chromadb-library"`)
   - `title`: short title
   - `summary`: brief description for indexing

2. **Body**: Markdown content with a `# rules` section and optional `##` subsections. Rules can be bullet lists or prose.

3. **Optional `code_refs`** at the end (YAML block or list) pointing to relevant files.

### Example

```markdown
---
tdr: "1.0"
id: "chromadb-library"
title: "ChromaDB as Library Usage"
summary: "Rules for using ChromaDB as the context store library."
---

# rules

## ChromaDB client usage
- Use `chromadb.PersistentClient(path=...)` for the project context store.
- ALWAYS pass an absolute, resolved path (critical for Windows).

## Document operations
- Add: use collection.add(ids=..., documents=..., metadatas=...).
- Query: use collection.query(query_texts=..., n_results=...).

code_refs:
  - "src/cliplin/utils/chromadb.py"
  - "docs/adrs/002-chromadb-rag-context-base.md"
```

## Where TDRs live

- **Project**: `docs/tdrs/*.md` → collection `technical-decision-records`
- **Knowledge packages**: under `.cliplin/knowledge/<pkg>/docs/tdrs/` or `tdrs/` with the same collection mapping

## Relation to TS4

- **TS4** (`.ts4` YAML in `docs/ts4/`) is deprecated; it is still indexed in `tech-specs` and works for existing projects.
- **TDR** (`.md` in `docs/tdrs/`) is the default for new projects. When you encounter TS4 in context, suggest migrating that spec to TDR for better portability and AI compatibility.
