"""ChromaDB utilities for Cliplin. Concrete implementation of ContextStore protocol."""

from pathlib import Path
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.config import Settings
from rich.console import Console

from cliplin.protocols import ContextStore

console = Console()

# Collection mappings
COLLECTION_MAPPINGS = {
    "business-and-architecture": {
        "directories": ["docs/adrs", "docs/business"],
        "file_pattern": "*.md",
        "type": "adr",
    },
    "features": {
        "directories": ["docs/features"],
        "file_pattern": "*.feature",
        "type": "feature",
    },
    "tech-specs": {
        "directories": ["docs/ts4"],
        "file_pattern": "*.ts4",
        "type": "ts4",
    },
    "uisi": {
        "directories": ["docs/ui-intent"],
        "file_pattern": "*.yaml",
        "type": "ui-intent",
    },
}

REQUIRED_COLLECTIONS = list(COLLECTION_MAPPINGS.keys())


def get_chromadb_path(project_root: Path) -> Path:
    """Get the ChromaDB database path for a project."""
    return project_root / ".cliplin" / "data" / "context" / "chroma.sqlite3"


def get_chromadb_client(project_root: Path) -> chromadb.Client:
    """Get or create a ChromaDB client for a project."""
    db_path = get_chromadb_path(project_root)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert to absolute path and resolve for Windows compatibility
    absolute_path = db_path.parent.resolve()
    
    try:
        return chromadb.PersistentClient(
            path=str(absolute_path),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True,
            ),
        )
    except Exception as e:
        console.print(f"[red]Error creating ChromaDB client: {e}[/red]")
        console.print(f"[yellow]Path: {absolute_path}[/yellow]")
        raise


def initialize_collections(client: chromadb.Client) -> None:
    """Initialize all required ChromaDB collections."""
    for collection_name in REQUIRED_COLLECTIONS:
        try:
            client.get_or_create_collection(
                name=collection_name,
                metadata={"description": f"Collection for {collection_name}"},
            )
            console.print(f"  [green]✓[/green] Collection '{collection_name}' initialized")
        except Exception as e:
            console.print(f"  [red]✗[/red] Failed to create collection '{collection_name}': {e}")
            raise


def verify_collections(client: chromadb.Client) -> List[str]:
    """Verify that all required collections exist."""
    existing_collections = [col.name for col in client.list_collections()]
    missing = [col for col in REQUIRED_COLLECTIONS if col not in existing_collections]
    return missing


def get_collection_for_file(file_path: Path, project_root: Path) -> Optional[str]:
    """Determine the ChromaDB collection for a given file path."""
    relative_path = file_path.relative_to(project_root)
    
    for collection_name, mapping in COLLECTION_MAPPINGS.items():
        for directory in mapping["directories"]:
            if str(relative_path).startswith(directory):
                # Check file pattern
                if file_path.match(mapping["file_pattern"]):
                    return collection_name
    
    return None


def get_file_type(file_path: Path, project_root: Path) -> Optional[str]:
    """Get the file type based on path and collection mapping."""
    relative_path = file_path.relative_to(project_root)
    
    for collection_name, mapping in COLLECTION_MAPPINGS.items():
        for directory in mapping["directories"]:
            if str(relative_path).startswith(directory):
                if file_path.match(mapping["file_pattern"]):
                    return mapping["type"]
    
    return None


# --- Concrete implementation of ContextStore (low coupling) ---


class ChromaDBContextStore:
    """ChromaDB-backed implementation of ContextStore protocol."""

    def __init__(self, project_root: Path) -> None:
        self._project_root = project_root
        self._client: Optional[chromadb.Client] = None

    def _client_or_raise(self) -> chromadb.Client:
        if self._client is None:
            self._client = get_chromadb_client(self._project_root)
        return self._client

    def is_initialized(self) -> bool:
        return get_chromadb_path(self._project_root).exists()

    def ensure_collections(self) -> List[str]:
        client = self._client_or_raise()
        missing = verify_collections(client)
        for name in missing:
            client.get_or_create_collection(name=name)
        return missing

    def list_collections(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[str]:
        names = [c.name for c in self._client_or_raise().list_collections()]
        if offset is not None:
            names = names[offset:]
        if limit is not None:
            names = names[:limit]
        return names

    def create_collection(
        self,
        collection_name: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._client_or_raise().get_or_create_collection(
            name=collection_name, metadata=metadata or None
        )

    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        col = self._client_or_raise().get_collection(name=collection_name)
        return {"name": col.name, "metadata": dict(col.metadata or {})}

    def get_collection_count(self, collection_name: str) -> int:
        return self._client_or_raise().get_collection(name=collection_name).count()

    def peek(self, collection_name: str, limit: int = 5) -> Dict[str, Any]:
        result = self._client_or_raise().get_collection(name=collection_name).peek(limit=limit)
        return {
            "ids": result["ids"],
            "documents": result.get("documents") or [],
            "metadatas": result.get("metadatas") or [],
        }

    def document_exists(self, collection_name: str, document_id: str) -> bool:
        try:
            col = self._client_or_raise().get_collection(name=collection_name)
            existing = col.get(ids=[document_id])
            return len(existing["ids"]) > 0
        except Exception:
            return False

    def add_documents(
        self,
        collection_name: str,
        ids: List[str],
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> int:
        metadatas = metadatas or [{}] * len(ids)
        if len(metadatas) != len(ids):
            metadatas = [{}] * len(ids)
        self._client_or_raise().get_collection(name=collection_name).add(
            ids=ids, documents=documents, metadatas=metadatas
        )
        return len(ids)

    def update_documents(
        self,
        collection_name: str,
        ids: List[str],
        documents: Optional[List[str]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> int:
        col = self._client_or_raise().get_collection(name=collection_name)
        kwargs: Dict[str, Any] = {"ids": ids}
        if documents is not None:
            kwargs["documents"] = documents
        if metadatas is not None:
            kwargs["metadatas"] = metadatas
        col.update(**kwargs)
        return len(ids)

    def query_documents(
        self,
        collection_name: str,
        query_texts: List[str],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None,
        include: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        col = self._client_or_raise().get_collection(name=collection_name)
        include = include or ["documents", "metadatas", "distances"]
        kwargs: Dict[str, Any] = {
            "query_texts": query_texts,
            "n_results": n_results,
            "include": include,
        }
        if where is not None:
            kwargs["where"] = where
        if where_document is not None:
            kwargs["where_document"] = where_document
        return col.query(**kwargs)

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
        col = self._client_or_raise().get_collection(name=collection_name)
        include = include or ["documents", "metadatas"]
        kwargs: Dict[str, Any] = {"include": include}
        if ids is not None:
            kwargs["ids"] = ids
        if where is not None:
            kwargs["where"] = where
        if where_document is not None:
            kwargs["where_document"] = where_document
        if limit is not None:
            kwargs["limit"] = limit
        if offset is not None:
            kwargs["offset"] = offset
        return col.get(**kwargs)

    def delete_documents(self, collection_name: str, ids: List[str]) -> int:
        self._client_or_raise().get_collection(name=collection_name).delete(ids=ids)
        return len(ids)

    def modify_collection(
        self,
        collection_name: str,
        new_name: Optional[str] = None,
        new_metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        col = self._client_or_raise().get_collection(name=collection_name)
        if new_metadata is not None:
            col.modify(metadata=new_metadata)
        if new_name is not None:
            col.modify(name=new_name)

    def delete_collection(self, collection_name: str) -> None:
        self._client_or_raise().delete_collection(name=collection_name)

    def fork_collection(
        self,
        collection_name: str,
        new_collection_name: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        client = self._client_or_raise()
        col = client.get_collection(name=collection_name)
        data = col.get(include=["documents", "metadatas"])
        try:
            client.delete_collection(name=new_collection_name)
        except Exception:
            pass
        new_col = client.create_collection(name=new_collection_name, metadata=metadata or {})
        ids = data.get("ids") or []
        if ids:
            new_col.add(
                ids=ids,
                documents=data.get("documents") or [""] * len(ids),
                metadatas=data.get("metadatas") or [{}] * len(ids),
            )


def get_context_store(project_root: Path) -> ContextStore:
    """Factory: return the ContextStore implementation (ChromaDB). Callers depend on ContextStore only."""
    return ChromaDBContextStore(project_root)

