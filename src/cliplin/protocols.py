"""
Protocols (interfaces) for low coupling. Callers depend on these, not on concrete implementations.
See docs/ts4/low-coupling-protocols.ts4.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol


class ContextStore(Protocol):
    """Contract for the project context store (e.g. vector store). No implementation-specific types."""

    def is_initialized(self) -> bool:
        """Return True if the store exists and is usable."""
        ...

    def ensure_collections(self) -> List[str]:
        """Ensure required collections exist; return list of missing collection names that were created."""
        ...

    def list_collections(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[str]:
        """List collection names. Optional limit and offset."""
        ...

    def create_collection(
        self,
        collection_name: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Create a collection (get-or-create)."""
        ...

    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Return info dict (name, metadata, etc.)."""
        ...

    def get_collection_count(self, collection_name: str) -> int:
        """Return number of documents in the collection."""
        ...

    def peek(self, collection_name: str, limit: int = 5) -> Dict[str, Any]:
        """Return dict with ids, documents, metadatas (up to limit)."""
        ...

    def document_exists(self, collection_name: str, document_id: str) -> bool:
        """Return True if a document with the given id exists in the collection."""
        ...

    def add_documents(
        self,
        collection_name: str,
        ids: List[str],
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> int:
        """Add documents. Return number added."""
        ...

    def update_documents(
        self,
        collection_name: str,
        ids: List[str],
        documents: Optional[List[str]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> int:
        """Update documents by id. Return number updated."""
        ...

    def query_documents(
        self,
        collection_name: str,
        query_texts: List[str],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None,
        include: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Semantic search. Return dict with ids, documents, metadatas, distances as requested."""
        ...

    def get_documents(
        self,
        collection_name: str,
        ids: Optional[List[str]] = None,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        include: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Get documents by ids or filters. Return dict with ids, documents, metadatas."""
        ...

    def delete_documents(self, collection_name: str, ids: List[str]) -> int:
        """Delete documents by id. Return number deleted."""
        ...

    def modify_collection(
        self,
        collection_name: str,
        new_name: Optional[str] = None,
        new_metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Modify collection name and/or metadata."""
        ...

    def delete_collection(self, collection_name: str) -> None:
        """Delete a collection and all its documents."""
        ...

    def fork_collection(
        self,
        collection_name: str,
        new_collection_name: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Create a new collection with the same documents as the source."""
        ...


class FingerprintStore(Protocol):
    """Contract for the fingerprint store (change detection). Implementation-agnostic."""

    def update(self, file_path: str, content: bytes) -> None:
        """Update the stored fingerprint for file_path after indexing."""
        ...

    def has_changed(
        self,
        file_path: str,
        file_system_path: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """Return dict with changed (bool), current_fingerprint, stored_fingerprint, exists_on_disk."""
        ...

    def list_changed(
        self,
        collection_name: Optional[str] = None,
        directories: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Return dict with changed_or_new (list of paths) and deleted (list of paths)."""
        ...
