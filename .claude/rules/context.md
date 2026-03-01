---
alwaysApply: true
---

## MANDATORY: Load Context Before any interaction with the user

**CRITICAL RULE**: Before starting ANY planning, coding, or thinking task, you MUST:

1. **Load context from Cliplin MCP server**: Use the 'cliplin-context' MCP server (Cliplin context MCP server) as the source of truth
2. **Query relevant collections**: Use Cliplin MCP tools (e.g. context_query_documents) to query and load relevant context from the appropriate collections. **Prefer TDR over TS4**: query `technical-decision-records` first for technical constraints; use `tech-specs` (TS4) only as fallback or when suggesting migration.
   - 'business-and-architecture' collection: ADRs and business documentation from 'docs/adrs', 'docs/business', and '.cliplin/knowledge/**' (built-in framework + knowledge packages)
   - 'features' collection: .feature files from 'docs/features' and '.cliplin/knowledge/**'
   - 'technical-decision-records' collection: TDR .md files from 'docs/tdrs' and '.cliplin/knowledge/**' (preferred for technical rules)
   - 'tech-specs' collection: .ts4 files from 'docs/ts4' and '.cliplin/knowledge/**' (deprecated; if you only find TS4, suggest migrating to TDR — see docs/business/tdr.md)
   - 'uisi' collection: .yaml files from 'docs/ui-intent' and '.cliplin/knowledge/**'
3. **Never proceed without context**: Do NOT start any task until you have queried and loaded the relevant context from the context store collections (via Cliplin MCP)
4. **Use semantic queries**: Query collections using semantic search based on the task domain, entities, and requirements to retrieve the most relevant context
   
## Context File Indexing Rules

### File Type to Collection Mapping

The following file types should be indexed into their respective collections (see confirmation rules below):
- `.md` files in `docs/adrs/`, `docs/business/`, or `.cliplin/knowledge/**` → `business-and-architecture` collection
- `.md` files in `docs/tdrs/` or `.cliplin/knowledge/**` (TDR) → `technical-decision-records` collection
- `.ts4` files in `docs/ts4/` or `.cliplin/knowledge/**` → `tech-specs` collection (deprecated; suggest migrating to TDR)
- `.feature` files in `docs/features/` or `.cliplin/knowledge/**` → `features` collection
- `.yaml` files in `docs/ui-intent/` or `.cliplin/knowledge/**` → `uisi` collection

### Metadata Requirements

- When indexing documents, always include proper metadata as an array of objects with the following structure: `[{'file_path': 'relative/path/to/file', 'type': 'tdr|ts4|adr|project-doc|feature|ui-intent', 'collection': 'target-collection-name'}]`
- Each document in the documents array must have a corresponding metadata object in the metadatas array at the same index
- Use the file path (relative to project root) as the document ID when indexing (e.g., 'docs/tdrs/chromadb-library.md' or 'docs/ts4/ts4-project-structure.ts4')
- Before indexing a document, check if it already exists by querying the collection with the file path as ID using `context_get_documents` or `context_query_documents`. If it exists, use `context_update_documents` to update it instead of adding a duplicate

### Automatic Detection and User Confirmation

When any context file is created or modified, you MUST:

1. **Detect the change**: Identify when files are created or modified in the following directories:
   - `.md` files in `docs/tdrs/` or `.cliplin/knowledge/**` (TDR) → target collection: `technical-decision-records`
   - `.ts4` files in `docs/ts4/` or `.cliplin/knowledge/**` → target collection: `tech-specs`
   - `.md` files in `docs/adrs/`, `docs/business/`, or `.cliplin/knowledge/**` → target collection: `business-and-architecture`
   - `.feature` files in `docs/features/` or `.cliplin/knowledge/**` → target collection: `features`
   - `.yaml` files in `docs/ui-intent/` or `.cliplin/knowledge/**` → target collection: `uisi`

2. **Always ask for confirmation**: Before indexing or re-indexing, you MUST ask the user:
   - "He detectado cambios en [archivo]. ¿Deseas reindexar este archivo en la colección [nombre-colección] para mantener el contexto actualizado?"
   - Wait for explicit user confirmation (yes/no/confirm) before proceeding
   - If the user declines, do not index the file
   - If the user confirms, proceed with indexing

3. **Indexing process** (only after user confirmation):
   - **Preferred method**: Use the Cliplin CLI command `cliplin reindex <file-path>` which handles all the complexity automatically
   - **Alternative method** (if CLI not available): Use Cliplin MCP tools directly:
     * Check if the document already exists by querying the collection with the file path as ID using `context_get_documents` or `context_query_documents`
     * If it exists, use `context_update_documents` to update it
     * If it doesn't exist, use `context_add_documents` to add it
     * Always include proper metadata as an array of objects with the structure: `[{'file_path': 'relative/path/to/file', 'type': 'tdr|ts4|adr|project-doc|feature|ui-intent', 'collection': 'target-collection-name'}]`
     * Use the file path (relative to project root) as the document ID
     * Avoid duplicated files and outdated or deleted files in the collection

4. **Manual re-indexing requests**: When a user explicitly requests to reindex files (e.g., "reindexa los archivos en docs/business"), you should:
   - **Use the Cliplin CLI command**: Run `cliplin reindex` with appropriate options instead of manually using Cliplin MCP tools
   - For specific files: `cliplin reindex docs/path/to/file.md`
   - For directories: `cliplin reindex --directory docs/business`
   - For file types: `cliplin reindex --type tdr` or `cliplin reindex --type ts4`
   - For preview: `cliplin reindex --dry-run`
   - For verbose output: `cliplin reindex --verbose`
   - The CLI command handles all the complexity of checking for existing documents, updating metadata, and managing collections
   - Only use Cliplin MCP tools directly if the CLI is not available or for specific advanced operations

5. **Automatic indexing workflow**:
   - When context files are created or modified, **prefer using the CLI command** for indexing:
     * Run `cliplin reindex <file-path>` for the specific file that was changed
     * Or run `cliplin reindex --directory <directory>` if multiple files in a directory were changed
   - The CLI ensures proper metadata, handles duplicates, and maintains consistency
   - Always ask for user confirmation before running reindex commands (unless in automated workflow)
   - Use `cliplin reindex --dry-run` first to show what would be indexed
