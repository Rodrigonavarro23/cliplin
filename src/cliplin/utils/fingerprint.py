"""Fingerprint store for change detection. Concrete implementation of FingerprintStore protocol."""

import datetime
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from cliplin.protocols import FingerprintStore

# Encoding for all file I/O (see windows-compatibility-file-operations.ts4)
ENCODING = "utf-8"


def get_fingerprint_store_path(project_root: Path) -> Path:
    """Path to the fingerprint JSON file under context data directory."""
    return project_root / ".cliplin" / "data" / "context" / "fingerprints.json"


def compute_fingerprint(content: bytes) -> str:
    """Compute SHA-256 fingerprint of content. Deterministic."""
    return hashlib.sha256(content).hexdigest()


def load_fingerprint_store(project_root: Path) -> Dict[str, Dict[str, Any]]:
    """Load fingerprint store from disk. Returns dict mapping file_path -> {fingerprint, last_indexed_at?}."""
    path = get_fingerprint_store_path(project_root)
    if not path.exists():
        return {}
    try:
        data = path.read_text(encoding=ENCODING)
        return json.loads(data)
    except (json.JSONDecodeError, OSError):
        return {}


def save_fingerprint_store(
    project_root: Path, store: Dict[str, Dict[str, Any]]
) -> None:
    """Persist fingerprint store to disk."""
    path = get_fingerprint_store_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(store, indent=2), encoding=ENCODING)


def update_fingerprint(
    project_root: Path,
    file_path: str,
    content: Optional[bytes] = None,
    file_system_path: Optional[Path] = None,
) -> None:
    """
    Update the fingerprint store for a document after indexing.
    Either pass content (bytes) or file_system_path to read from disk.
    file_path should be relative to project root (e.g. docs/ts4/example.ts4).
    """
    if content is None and file_system_path is None:
        raise ValueError("Provide content or file_system_path")
    if content is None:
        content = file_system_path.read_bytes()
    fp = compute_fingerprint(content)
    store = load_fingerprint_store(project_root)
    store[file_path] = {
        "fingerprint": fp,
        "last_indexed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    save_fingerprint_store(project_root, store)


def has_document_changed(
    project_root: Path,
    file_path: str,
    file_system_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Check if a document has changed since last index.
    file_path: relative path (e.g. docs/ts4/example.ts4).
    Returns dict with keys: changed (bool), current_fingerprint (str|None), stored_fingerprint (str|None), exists_on_disk (bool).
    """
    path = file_system_path or (project_root / file_path)
    store = load_fingerprint_store(project_root)
    stored = store.get(file_path)

    if not path.exists():
        return {
            "changed": True,
            "current_fingerprint": None,
            "stored_fingerprint": stored.get("fingerprint") if stored else None,
            "exists_on_disk": False,
        }

    current_fp = compute_fingerprint(path.read_bytes())
    stored_fp = stored.get("fingerprint") if stored else None

    return {
        "changed": stored_fp is None or current_fp != stored_fp,
        "current_fingerprint": current_fp,
        "stored_fingerprint": stored_fp,
        "exists_on_disk": True,
    }


def _collect_context_files(
    project_root: Path,
    collection_name: Optional[str] = None,
    directories: Optional[List[str]] = None,
) -> List[Path]:
    """Return list of context file paths to consider. Uses COLLECTION_MAPPINGS."""
    from cliplin.utils.chromadb import COLLECTION_MAPPINGS

    if collection_name:
        if collection_name not in COLLECTION_MAPPINGS:
            return []
        mapping = COLLECTION_MAPPINGS[collection_name]
        files: List[Path] = []
        for d in mapping["directories"]:
            dir_path = project_root / d
            if dir_path.exists():
                files.extend(dir_path.rglob(mapping["file_pattern"]))
        return [f for f in files if f.is_file()]
    if directories:
        files = []
        for d in directories:
            dir_path = project_root / d
            if not dir_path.exists():
                continue
            for mapping in COLLECTION_MAPPINGS.values():
                if d in mapping["directories"]:
                    files.extend(dir_path.rglob(mapping["file_pattern"]))
                    break
        return [f for f in files if f.is_file()]
    # All context files
    files = []
    for mapping in COLLECTION_MAPPINGS.values():
        for d in mapping["directories"]:
            dir_path = project_root / d
            if dir_path.exists():
                files.extend(dir_path.rglob(mapping["file_pattern"]))
    return [f for f in files if f.is_file()]


def list_changed_documents(
    project_root: Path,
    collection_name: Optional[str] = None,
    directories: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    List file paths that need reindexing: new (no fingerprint) or changed (fingerprint differs).
    Optionally scope by collection_name (e.g. tech-specs) or directories (e.g. [docs/ts4, docs/features]).
    Returns dict with keys: changed_or_new (list of paths), deleted (list of paths in store but missing on disk).
    """
    store = load_fingerprint_store(project_root)
    files_to_check = _collect_context_files(project_root, collection_name, directories)

    changed_or_new: List[str] = []
    seen_paths = set()
    for f in files_to_check:
        rel = str(f.relative_to(project_root))
        if rel in seen_paths:
            continue
        seen_paths.add(rel)
        result = has_document_changed(project_root, rel, f)
        if result["changed"]:
            changed_or_new.append(rel)

    deleted: List[str] = []
    for stored_path in store:
        full = project_root / stored_path
        if not full.exists():
            deleted.append(stored_path)

    return {"changed_or_new": sorted(changed_or_new), "deleted": sorted(deleted)}


# --- Concrete implementation of FingerprintStore (low coupling) ---


class JsonFingerprintStore:
    """JSON-backed implementation of FingerprintStore protocol."""

    def __init__(self, project_root: Path) -> None:
        self._project_root = project_root

    def update(self, file_path: str, content: bytes) -> None:
        update_fingerprint(self._project_root, file_path, content=content)

    def has_changed(
        self,
        file_path: str,
        file_system_path: Optional[Path] = None,
    ) -> Dict[str, Any]:
        return has_document_changed(
            self._project_root, file_path, file_system_path=file_system_path
        )

    def list_changed(
        self,
        collection_name: Optional[str] = None,
        directories: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        return list_changed_documents(
            self._project_root,
            collection_name=collection_name,
            directories=directories,
        )


def get_fingerprint_store(project_root: Path) -> FingerprintStore:
    """Factory: return the FingerprintStore implementation (JSON). Callers depend on FingerprintStore only."""
    return JsonFingerprintStore(project_root)
