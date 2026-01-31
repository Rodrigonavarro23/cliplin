"""
Cliplin Storage MCP server. Exposes context store and fingerprint tools via protocols.
Uses project root = cwd (Cursor runs 'cliplin mcp' from project root).
See docs/ts4/low-coupling-protocols.ts4.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

from cliplin.protocols import ContextStore, FingerprintStore
from cliplin.utils.chromadb import get_context_store
from cliplin.utils.fingerprint import get_fingerprint_store

MCP_INSTRUCTIONS = """Cliplin context server: semantic search over project specs (ADRs, features, TS4, UI intent).
Use chroma_query_documents to load relevant context before planning or coding. Collections: business-and-architecture, features, tech-specs, uisi.
Use chroma_list_changed_documents or chroma_check_document_changed for change detection. Never proceed without loading context from this server."""

mcp = FastMCP(
    "cliplin-context",
    instructions=MCP_INSTRUCTIONS,
    json_response=True,
)


def _project_root() -> Path:
    return Path.cwd()


def _get_store() -> ContextStore:
    return get_context_store(_project_root())


def _get_fingerprint_store() -> FingerprintStore:
    return get_fingerprint_store(_project_root())


def _ensure_db() -> None:
    if not _get_store().is_initialized():
        raise FileNotFoundError(
            "Context store is not initialized. Run 'cliplin init' first."
        )


# --- Collection tools ---


@mcp.tool()
def chroma_list_collections(
    limit: Optional[int] = None,
    offset: Optional[int] = None,
) -> str:
    """List all collection names in the context store. Optional limit and offset for pagination."""
    _ensure_db()
    names = _get_store().list_collections(limit=limit, offset=offset)
    return json.dumps({"collections": names})


@mcp.tool()
def chroma_create_collection(
    collection_name: str,
    embedding_function_name: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """Create a new collection (get-or-create). Optional embedding_function_name and metadata."""
    _ensure_db()
    meta = dict(metadata or {})
    if embedding_function_name:
        meta["embedding_function"] = embedding_function_name
    _get_store().create_collection(collection_name, metadata=meta or None)
    return json.dumps({"status": "ok", "collection": collection_name})


@mcp.tool()
def chroma_get_collection_info(collection_name: str) -> str:
    """Get information about a collection (name, metadata, etc.)."""
    _ensure_db()
    info = _get_store().get_collection_info(collection_name)
    return json.dumps(info)


@mcp.tool()
def chroma_get_collection_count(collection_name: str) -> str:
    """Get the number of documents in a collection."""
    _ensure_db()
    count = _get_store().get_collection_count(collection_name)
    return json.dumps({"count": count})


@mcp.tool()
def chroma_peek_collection(collection_name: str, limit: int = 5) -> str:
    """Peek at documents in a collection. Returns up to `limit` documents (default 5)."""
    _ensure_db()
    out = _get_store().peek(collection_name, limit=limit)
    return json.dumps(out)


@mcp.tool()
def chroma_add_documents(
    collection_name: str,
    documents: List[str],
    ids: List[str],
    metadatas: Optional[List[Dict[str, Any]]] = None,
) -> str:
    """Add documents to a collection. Requires documents and ids lists of the same length. Optional metadatas per document."""
    _ensure_db()
    store = _get_store()
    fp_store = _get_fingerprint_store()
    if len(documents) != len(ids):
        return json.dumps({"error": "documents and ids must have the same length"})
    n = store.add_documents(collection_name, ids, documents, metadatas=metadatas)
    for i, doc_id in enumerate(ids):
        try:
            fp_store.update(doc_id, documents[i].encode("utf-8"))
        except Exception:
            pass
    return json.dumps({"added": n})


@mcp.tool()
def chroma_query_documents(
    collection_name: str,
    query_texts: List[str],
    n_results: int = 5,
    where: Optional[Dict[str, Any]] = None,
    where_document: Optional[Dict[str, Any]] = None,
    include: Optional[List[str]] = None,
) -> str:
    """Semantic search in a collection. query_texts: list of query strings. n_results per query. Optional where (metadata filter) and where_document (content filter)."""
    _ensure_db()
    result = _get_store().query_documents(
        collection_name, query_texts, n_results=n_results,
        where=where, where_document=where_document, include=include,
    )
    return json.dumps(result)


@mcp.tool()
def chroma_get_documents(
    collection_name: str,
    ids: Optional[List[str]] = None,
    where: Optional[Dict[str, Any]] = None,
    where_document: Optional[Dict[str, Any]] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    include: Optional[List[str]] = None,
) -> str:
    """Get documents by ids or by metadata/document filters. Optional limit and offset."""
    _ensure_db()
    result = _get_store().get_documents(
        collection_name, ids=ids, where=where, where_document=where_document,
        limit=limit, offset=offset, include=include,
    )
    return json.dumps(result)


@mcp.tool()
def chroma_update_documents(
    collection_name: str,
    ids: List[str],
    documents: Optional[List[str]] = None,
    metadatas: Optional[List[Dict[str, Any]]] = None,
) -> str:
    """Update documents by id. Provide ids and optionally documents and/or metadatas (same length as ids)."""
    _ensure_db()
    store = _get_store()
    fp_store = _get_fingerprint_store()
    n = store.update_documents(collection_name, ids, documents=documents, metadatas=metadatas)
    if documents is not None:
        for i, doc_id in enumerate(ids):
            if i < len(documents):
                try:
                    fp_store.update(doc_id, documents[i].encode("utf-8"))
                except Exception:
                    pass
    return json.dumps({"updated": n})


@mcp.tool()
def chroma_delete_documents(collection_name: str, ids: List[str]) -> str:
    """Delete documents from a collection by id."""
    _ensure_db()
    n = _get_store().delete_documents(collection_name, ids)
    return json.dumps({"deleted": n})


@mcp.tool()
def chroma_modify_collection(
    collection_name: str,
    new_name: Optional[str] = None,
    new_metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """Modify a collection's name and/or metadata."""
    _ensure_db()
    try:
        _get_store().modify_collection(collection_name, new_name=new_name, new_metadata=new_metadata)
    except Exception as e:
        return json.dumps({"error": str(e), "metadata_updated": new_metadata is not None})
    return json.dumps({"status": "ok"})


@mcp.tool()
def chroma_delete_collection(collection_name: str) -> str:
    """Delete a collection and all its documents."""
    _ensure_db()
    _get_store().delete_collection(collection_name)
    return json.dumps({"status": "deleted", "collection": collection_name})


@mcp.tool()
def chroma_fork_collection(
    collection_name: str,
    new_collection_name: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """Create a new collection with the same documents as the source. Optional metadata for the new collection."""
    _ensure_db()
    _get_store().fork_collection(collection_name, new_collection_name, metadata=metadata)
    return json.dumps({"status": "ok", "new_collection": new_collection_name})


# --- Change detection tools ---


@mcp.tool()
def chroma_check_document_changed(file_path: str) -> str:
    """Check if a document (by relative file path, e.g. docs/ts4/example.ts4) has changed since last index. Uses fingerprint store."""
    result = _get_fingerprint_store().has_changed(file_path)
    return json.dumps(result)


@mcp.tool()
def chroma_list_changed_documents(
    collection_name: Optional[str] = None,
    directories: Optional[List[str]] = None,
) -> str:
    """List file paths that need reindexing (changed or new). Optionally scope by collection_name or directories (e.g. [docs/ts4, docs/features]). Returns changed_or_new and deleted lists."""
    result = _get_fingerprint_store().list_changed(collection_name=collection_name, directories=directories)
    return json.dumps(result)


def run_mcp_server() -> None:
    """Run the MCP server with stdio transport (for Cursor/Claude)."""
    mcp.run(transport="stdio")
