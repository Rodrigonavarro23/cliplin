Feature: Cliplin Storage MCP
  As an AI tool or developer
  I want Cliplin to expose a storage MCP server
  So that I can index, search, count, and manage documents in the project context store via MCP without depending on a specific storage implementation

  Background:
    Given I have the Cliplin CLI tool installed
    And I have initialized a Cliplin project with an AI tool (e.g. cursor or claude-desktop)
    And the project context store is initialized at the project data path
    And the MCP server configuration includes the Cliplin storage MCP server

  @status:implemented
  @changed:2025-01-30
  Scenario: List all collections in the context store
    Given the storage MCP server is running and connected to the project context store
    When I invoke the MCP tool to list collections
    Then the MCP should return the names of all existing collections
    And the response may support optional pagination (limit and offset)
    And if the store has no collections, the MCP should return an empty list or a defined empty indicator
    And the MCP should not require the caller to know implementation details of the store

  @status:implemented
  @changed:2025-01-30
  Scenario: Create a new collection
    Given the storage MCP server is running and connected to the project context store
    And a collection with name "my-collection" does not exist
    When I invoke the MCP tool to create a collection with name "my-collection"
    Then the MCP should create the collection in the context store
    And the MCP may accept optional parameters such as embedding function name and metadata
    And the MCP should return a success or confirmation
    And the new collection should appear when listing collections
    And if a collection with the same name already exists, the MCP should report an error or use get-or-create semantics as documented

  @status:implemented
  @changed:2025-01-30
  Scenario: Get collection information
    Given the storage MCP server is running and connected to the project context store
    And a collection named "tech-specs" exists
    When I invoke the MCP tool to get collection info for "tech-specs"
    Then the MCP should return information about the collection
    And the information may include name, metadata, and embedding configuration
    And if the collection does not exist, the MCP should return an error or clear failure indication

  @status:implemented
  @changed:2025-01-30
  Scenario: Get document count in a collection
    Given the storage MCP server is running and connected to the project context store
    And a collection named "features" exists
    And the collection contains some number of documents
    When I invoke the MCP tool to get the document count for collection "features"
    Then the MCP should return the number of documents in that collection
    And the count should match the actual number of indexed documents
    And if the collection does not exist, the MCP should return an error

  @status:implemented
  @changed:2025-01-30
  Scenario: Peek at documents in a collection
    Given the storage MCP server is running and connected to the project context store
    And a collection named "business-and-architecture" exists and contains documents
    When I invoke the MCP tool to peek into the collection with a limit of 5
    Then the MCP should return up to the requested number of documents (or fewer if the collection has less)
    And the response should include document content and optionally metadata and IDs
    And the peek should not remove or alter documents
    And the MCP may support a default limit when limit is not specified

  @status:implemented
  @changed:2025-01-30
  Scenario: Add documents to a collection (index)
    Given the storage MCP server is running and connected to the project context store
    And a collection named "tech-specs" exists
    When I invoke the MCP tool to add documents to "tech-specs" with:
      | documents | ids | metadatas (optional) |
      | ["Document A text", "Document B text"] | ["id-1", "id-2"] | optional metadata per document |
    Then the MCP should index the documents into the collection
    And each document should be associated with the given ID
    And optional metadata should be stored and available for filtering
    And the document count for the collection should increase by the number of documents added
    And the MCP should return a confirmation of how many documents were added
    And the store should compute or accept embeddings for semantic search as per collection configuration

  @status:implemented
  @changed:2025-01-30
  Scenario: Query documents by semantic search
    Given the storage MCP server is running and connected to the project context store
    And a collection named "features" exists and contains indexed documents
    When I invoke the MCP tool to query the collection with query texts and number of results
    Then the MCP should perform semantic search over the collection
    And the MCP should return the most similar documents to each query text
    And the response should include documents, metadata, and distances (or similarity scores) as configured
    And the MCP may support optional metadata filters to restrict results (e.g. by file_path or type)
    And the MCP may support optional document content filters (e.g. contains, regex)
    And the number of results per query should respect the requested n_results parameter

  @status:implemented
  @changed:2025-01-30
  Scenario: Get documents by IDs or filters
    Given the storage MCP server is running and connected to the project context store
    And a collection named "uisi" exists and contains documents with known IDs
    When I invoke the MCP tool to get documents from the collection by IDs or by metadata/document filters
    Then the MCP should return the matching documents with their metadata
    And when filtering by metadata, the MCP should support equality and comparison operators as documented
    And when filtering by document content, the MCP may support operators such as contains or regex
    And the response may support limit and offset for pagination
    And if no documents match, the MCP should return an empty result set

  @status:implemented
  @changed:2025-01-30
  Scenario: Update documents in a collection
    Given the storage MCP server is running and connected to the project context store
    And a collection named "business-and-architecture" exists
    And the collection contains a document with ID "docs/adrs/001-example.md"
    When I invoke the MCP tool to update that document with new content, metadata, or embeddings
    Then the MCP should update the existing document by ID
    And the document count should not change
    And subsequent get or query operations should return the updated content and metadata
    And the MCP should return a confirmation of how many documents were updated
    And if the ID does not exist, the MCP should report an error and not create a new document unless documented otherwise

  @status:implemented
  @changed:2025-01-30
  Scenario: Delete documents from a collection
    Given the storage MCP server is running and connected to the project context store
    And a collection named "tech-specs" exists and contains documents with known IDs
    When I invoke the MCP tool to delete documents by a list of IDs
    Then the MCP should remove those documents from the collection
    And the document count should decrease by the number of deleted documents
    And the MCP should return a confirmation of how many documents were deleted
    And get or query for those IDs should no longer return those documents
    And if an ID does not exist, the MCP may ignore it or report it; behavior should be documented

  @status:implemented
  @changed:2025-01-30
  Scenario: Modify collection name or metadata
    Given the storage MCP server is running and connected to the project context store
    And a collection named "old-name" exists
    When I invoke the MCP tool to modify the collection with an optional new name and optional new metadata
    Then the MCP should update the collection name and/or metadata as requested
    And listing collections should reflect the new name if changed
    And get collection info should return the updated metadata
    And existing documents in the collection should remain unchanged

  @status:new
  Scenario: Delete a collection
    Given the storage MCP server is running and connected to the project context store
    And a collection named "temp-collection" exists
    When I invoke the MCP tool to delete the collection "temp-collection"
    Then the MCP should remove the collection and all its documents from the store
    And listing collections should no longer include "temp-collection"
    And any subsequent operation on that collection name should fail with a clear error
    And the MCP should return a confirmation of deletion

  @status:implemented
  @changed:2025-01-30
  Scenario: Fork a collection
    Given the storage MCP server is running and connected to the project context store
    And a collection named "features" exists and contains documents
    When I invoke the MCP tool to fork "features" into a new collection named "features-backup"
    Then the MCP should create a new collection with the requested name
    And the new collection should contain the same documents (and embeddings) as the source collection
    And the source collection should remain unchanged
    And optional metadata may be added to the new collection
    And the MCP should return a success or confirmation

  @status:new
  Scenario: Query with metadata filter
    Given the storage MCP server is running and connected to the project context store
    And a collection named "tech-specs" exists with documents that have metadata "type" and "file_path"
    When I invoke the MCP tool to query the collection with a query text and a metadata filter (e.g. type equals "ts4")
    Then the MCP should perform semantic search only over documents matching the metadata filter
    And the returned documents should satisfy both similarity and filter criteria
    And the MCP should support at least equality filters; comparison and logical operators may be supported as documented

  @status:implemented
  @changed:2025-01-30
  Scenario: Storage MCP uses project context store path
    Given I have initialized a Cliplin project with an AI tool
    When the Cliplin storage MCP server is started by the AI tool
    Then the MCP server should be configured to use the project context store path (e.g. under .cliplin/data/context)
    And the same store should be used for all MCP storage operations in that project
    And no implementation-specific storage product name should be required in the feature contract; only "context store" and "storage MCP" semantics

  @status:implemented
  @changed:2025-01-30
  Scenario: Handle non-existent collection gracefully
    Given the storage MCP server is running and connected to the project context store
    And a collection named "non-existent" does not exist
    When I invoke any MCP tool that requires a collection name with "non-existent"
    Then the MCP should return a clear error indicating that the collection does not exist
    And the MCP should not create the collection unless the operation is explicitly a create or get-or-create
    And the error message should be actionable for the caller

  # --- Change detection (fingerprint store) ---
  # The system maintains a fingerprint store (e.g. file path -> hash) to detect whether
  # indexed documents have been updated on disk. Implementation may use a local JSON
  # file under the context data path (recommended for fast checks without querying the
  # vector store) or an internal meta-collection; behavior is equivalent from the caller's perspective.

  @status:implemented
  @changed:2025-01-30
  Scenario: Check if a document has been updated since last index
    Given the storage MCP server is running and connected to the project context store
    And a fingerprint store exists (e.g. mapping file path to hash or checksum)
    And a document at path "docs/ts4/example.ts4" was previously indexed and has a stored fingerprint
    When I invoke the MCP tool to check if the document at path "docs/ts4/example.ts4" has changed
    Then the MCP should compute the current fingerprint of the file (e.g. SHA-256 of content)
    And the MCP should compare it with the stored fingerprint for that path
    And the MCP should return whether the document has changed (e.g. true/false or status)
    And the MCP may return the stored fingerprint and current fingerprint for debugging
    And if the file no longer exists on disk, the MCP should report it as changed or removed
    And the check should not require loading document content from the vector store; only the fingerprint store and filesystem are used

  @status:implemented
  @changed:2025-01-30
  Scenario: Check if document has changed when file was modified on disk
    Given the storage MCP server is running and connected to the project context store
    And a fingerprint store exists with a stored fingerprint for "docs/ts4/my-spec.ts4"
    And the file "docs/ts4/my-spec.ts4" has been modified on disk since it was last indexed
    When I invoke the MCP tool to check if the document at path "docs/ts4/my-spec.ts4" has changed
    Then the MCP should compute the current fingerprint of the file
    And the MCP should determine that the current fingerprint differs from the stored fingerprint
    And the MCP should return that the document has changed (e.g. needs reindexing)
    And the caller can use this result to decide whether to reindex the document

  @status:implemented
  @changed:2025-01-30
  Scenario: Check if document is unchanged when file was not modified
    Given the storage MCP server is running and connected to the project context store
    And a fingerprint store exists with a stored fingerprint for "docs/features/login.feature"
    And the file "docs/features/login.feature" has not been modified since it was last indexed
    When I invoke the MCP tool to check if the document at path "docs/features/login.feature" has changed
    Then the MCP should compute the current fingerprint of the file
    And the MCP should determine that the current fingerprint matches the stored fingerprint
    And the MCP should return that the document has not changed
    And the caller can skip reindexing for this document

  @status:implemented
  @changed:2025-01-30
  Scenario: List documents that need reindexing (by collection or directory)
    Given the storage MCP server is running and connected to the project context store
    And a fingerprint store exists with fingerprints for previously indexed documents
    And some context files have been modified on disk or are new (no stored fingerprint)
    When I invoke the MCP tool to list changed documents for collection "tech-specs" or for directories "docs/ts4", "docs/features"
    Then the MCP should return the list of file paths that have changed (current fingerprint differs from stored) or are new (no fingerprint)
    And the MCP may return paths that are in the fingerprint store but no longer exist on disk (deleted files) so the caller can remove them from the index
    And the result may be scoped by collection name, by directory list, or by file type
    And the MCP should not require reading document content from the vector store; comparison uses the fingerprint store and filesystem only
    And the caller can use this list to perform incremental reindexing (only changed or new documents)

  @status:implemented
  @changed:2025-01-30
  Scenario: Update fingerprint store after indexing a document
    Given the storage MCP server is running and connected to the project context store
    And a fingerprint store exists
    When a document is successfully added or updated in a collection (e.g. via add documents or update documents)
    Then the fingerprint store should be updated with the current fingerprint (e.g. SHA-256 of content) for that document path
    And the stored fingerprint should be associated with the document ID or file path used in the collection
    And optional metadata such as "last_indexed_at" may be stored
    So that subsequent "check if document has changed" or "list changed documents" calls are accurate
    And the update may be performed by the MCP as part of add/update, or by the indexing workflow; behavior should be documented

  @status:implemented
  @changed:2025-01-30
  Scenario: Fingerprint store location and persistence
    Given the project context store is initialized at the project data path (e.g. .cliplin/data/context)
    When the fingerprint store is used (read or write)
    Then the fingerprint store should live under the same project context data path
    And the fingerprint store should persist across MCP server restarts
    And the implementation may use a local file (e.g. JSON mapping file_path to fingerprint and optional metadata) for fast read/write without querying the vector store
    And the implementation may use an internal meta-collection in the same store if preferred; the contract is equivalent: path -> fingerprint, update after index, list changed documents
    And the fingerprint algorithm (e.g. SHA-256 of file content) should be deterministic so that the same file content always yields the same fingerprint
