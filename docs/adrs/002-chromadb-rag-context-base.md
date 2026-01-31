# ADR-002: ChromaDB as RAG and Context Store Base

## Status
Accepted

## Context

Systems that treat specifications as the source of truth (e.g. Spec-Driven Development) need a way to:

1. **Index** documentation of different kinds (text, and in the future images and other media).
2. **Search semantically**, not just by keywords, to retrieve the most relevant context for a given query or task.
3. **Separate by domain**: ADRs, features, technical specs, and UI specs should not live in a single bucket; queries should target the right collection.
4. **Persist locally**: context should live in the project (e.g. under a project data directory) without requiring external services.
5. **Share one store**: the same vector store should support both indexing workflows and query tools (CLI, MCP, or other consumers).

We evaluated using a vector database as the core of the system’s RAG. ChromaDB was chosen as the base for that RAG and for the context model.

## Decision

**Use ChromaDB as the base for RAG and as the context store**, leveraging its ability to index documents (and potentially images and other types), semantic search via embeddings, and its fit for a collection-based model aligned with documentation types.

### 1. ChromaDB as a RAG Foundation

- **Embeddings and semantic search**: ChromaDB stores vectors (embeddings) for documents. Queries are embedded into the same vector space, enabling similarity search by meaning, not exact text. This is the core of RAG: retrieve the most relevant chunks before generating a response.
- **Persistent storage**: ChromaDB’s `PersistentClient` writes to a directory on disk. A project can have one vector store per workspace, either versioned or excluded (e.g. via `.gitignore`) as needed.
- **Embedding flexibility**: ChromaDB supports default and custom embedding functions (local or API-based). The system can run without external APIs if required.

### 2. ChromaDB Capabilities: Documents, Images, and Beyond

- **Text documents**: ChromaDB indexes text by default. Documents are split (or used whole), embedded, and stored with optional metadata. Any text-based spec (Markdown, YAML, Gherkin, etc.) can be indexed and queried semantically.
- **Images and multimodal**: ChromaDB supports **multimodal embeddings** (e.g. via OpenCLIP): text and images share the same embedding space, so you can index images and search with text or with another image. Alternatively, images can be described with a vision model and the description indexed as text; semantic search then runs over that text. The choice of when to add image indexing is left to a later decision; ChromaDB’s architecture does not block it.
- **Other types**: Any content that can be turned into text or into vectors (via an embedding function) can be added to the same collection and metadata model.

### 3. Semantic Search and Filtering

- **Semantic query**: ChromaDB’s query API accepts text (or precomputed vectors) and returns the most similar documents by embedding distance. This directly feeds RAG: “return the most relevant context for this question.”
- **Metadata filtering**: ChromaDB supports filtering by metadata (`where`). This allows scoping queries by domain (e.g. only ADRs, only features), by file path, or by custom attributes. Combining semantic search with metadata filters yields “search within this collection for content about X.”
- **Where-document filters**: ChromaDB can also filter by document content (e.g. `$contains`, `$regex`), so hybrid workflows (metadata + content + semantic) are possible.

### 4. Fit for a Spec/Context-Driven System (e.g. Cliplin)

- **Collections by documentation type**: Instead of one large collection, use one collection per pillar (e.g. business-and-architecture, features, tech-specs, ui-intent). This keeps domains separate and lets query tools target the right collection.
- **Stable IDs and metadata**: Using a stable document ID (e.g. file path relative to project root) avoids duplicates and supports upserts. Metadata such as `file_path`, `type`, and `collection` enable traceability and selective updates. ChromaDB does not prescribe schema; the system defines it.
- **Standard ChromaDB operations**: Add, update, query, and delete use ChromaDB’s standard API. Indexing and refresh workflows are built on these primitives; no product-specific RAG API is required.
- **Single store**: The same ChromaDB instance can serve indexing pipelines and any consumer (CLI, MCP, scripts). One source of truth for context.

### 5. Change detection (fingerprint store)

To support incremental indexing and “has this document changed?” checks (e.g. “revisar si han ocurrido cambios en los ts4”), the system maintains a **fingerprint store**: a mapping from document path (or ID) to a content fingerprint (e.g. SHA-256 of file content).

- **Purpose**: Detect whether an indexed document has been updated on disk so that only changed or new files are reindexed; list documents that need reindexing by collection or directory.
- **Recommended implementation: local JSON file** under the project context data path (e.g. `.cliplin/data/context/fingerprints.json`), mapping `file_path` → `{ "fingerprint": "<sha256>", "last_indexed_at": "<iso8601>" }` (or equivalent).  
  **Rationale**: Change detection is read-heavy and should be fast. A single JSON read and in-memory comparison avoids opening the vector store or running embeddings. The fingerprint store is metadata about the filesystem, not user content; keeping it in a separate file avoids polluting the vector DB and keeps a simple, portable schema (easy to invalidate or migrate). Same permissions and path as the rest of the context data.
- **Alternative**: An internal meta-collection (e.g. a dedicated collection only for path → fingerprint) is possible and keeps everything in one store, but every “list changed” or “has changed?” check would require querying that collection; for many files, a single JSON file is cheaper and simpler.
- **Contract**: After each successful add or update of a document in a collection, the fingerprint store is updated with the current fingerprint for that path. MCP or CLI can expose “check if document has changed” and “list documents that need reindexing” using only the fingerprint store and the filesystem (no vector store read for the check). Fingerprint algorithm must be deterministic (e.g. SHA-256 of file content).

### 6. Technical Summary

| Aspect | Decision |
|--------|----------|
| Vector engine | ChromaDB (PersistentClient) |
| Storage | Project data directory (path resolved for cross-platform use) |
| Collections | One per documentation pillar (e.g. business-and-architecture, features, tech-specs, uisi) |
| Document ID | Stable identifier (e.g. relative file path) |
| Metadata | At least file_path, type, collection (system-defined) |
| Search | Semantic (embeddings) + optional metadata and content filters |
| Change detection | Fingerprint store (path → fingerprint); recommended: local JSON file under context data path |
| Future extension | Images/multimodal via OpenCLIP or text descriptions |

## Consequences

### Positive

- **RAG aligned with specs**: Context for AI comes from indexed specifications, not ad-hoc or scattered docs.
- **Intent-based search**: Semantic search supports queries like “how do we validate inputs?” or “what ADRs discuss persistence?” without relying on exact keywords.
- **Domain separation**: Collections keep ADRs, features, tech specs, and UI specs distinct and reduce noise.
- **Single store**: One ChromaDB instance for all indexing and query tools; no duplicated context store.
- **Extensibility**: The same model supports adding images or other types via multimodal embeddings or text descriptions.
- **Traceability**: Metadata (e.g. file_path) links retrieved chunks back to source files and supports selective refresh.
- **Change detection**: A fingerprint store (recommended: local JSON) allows fast “has this document changed?” and “list documents that need reindexing” without querying the vector store; incremental indexing stays cheap.

### Negative

- **ChromaDB dependency**: Switching to another vector store would require data migration and code changes.
- **Path handling**: On some platforms (e.g. Windows), paths must be resolved to absolute before passing to ChromaDB; this is a general integration concern.
- **Images not required**: Multimodal is supported by ChromaDB but optional; adding image indexing later implies defining formats, embedding function, and metadata conventions.

### Risks and Mitigations

- **Embedding consistency**: If the embedding function changes (e.g. different model or API), collections should be created or migrated with the same configuration to avoid mixing vector spaces.
- **Scale**: Large documentation sets mean more vectors; ChromaDB scales well for per-project local use; batch indexing and query patterns should remain reasonable.

## Notes

- This ADR complements **ADR-001** (collection management and ChromaDB usage patterns).
- When to add image indexing (e.g. diagrams in ADRs, wireframes in UI specs) is left to a future ADR or spec; ChromaDB’s architecture does not block it.
- References: [ChromaDB documentation](https://docs.trychroma.com/), [ChromaDB Multimodal Embeddings](https://docs.trychroma.com/docs/embeddings/multimodal).
