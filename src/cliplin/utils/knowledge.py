"""
Knowledge package utilities: cliplin.yaml knowledge section, path normalization, git clone + sparse checkout.
See docs/tdrs/knowledge-packages.md and docs/adrs/005-knowledge-packages.md.
"""

import re
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

CONFIG_FILENAME = "cliplin.yaml"

# Paths to materialize in a knowledge package repo (sparse checkout). Same semantics as project docs.
SPARSE_PATHS = [
    "docs/adrs",
    "docs/business",
    "docs/features",
    "docs/tdrs",
    "docs/ts4",
    "docs/ui-intent",
    "adrs",
    "business",
    "features",
    "tdrs",
    "ts4",
    "ui-intent",
    "rules",
    "skills",
    "templates",
]


def get_config_path(project_root: Path) -> Path:
    """Path to cliplin.yaml at project root."""
    return project_root / CONFIG_FILENAME


def load_config(project_root: Path) -> Dict[str, Any]:
    """Load cliplin.yaml; return dict (empty if missing or invalid)."""
    path = get_config_path(project_root)
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return dict(data) if isinstance(data, dict) else {}
    except (yaml.YAMLError, OSError):
        return {}


def save_config(project_root: Path, config: Dict[str, Any]) -> None:
    """Write cliplin.yaml preserving key order and other keys."""
    path = get_config_path(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def get_knowledge_packages(config: Dict[str, Any]) -> List[Dict[str, str]]:
    """Return list of knowledge entries from config (name, source, version)."""
    raw = config.get("knowledge")
    if not isinstance(raw, list):
        return []
    return [
        {"name": str(e.get("name", "")), "source": str(e.get("source", "")), "version": str(e.get("version", ""))}
        for e in raw
        if isinstance(e, dict) and e.get("name")
    ]


def add_knowledge_package_to_config(
    config: Dict[str, Any], name: str, source: str, version: str
) -> Dict[str, Any]:
    """Return new config with package appended to knowledge list. Does not mutate config."""
    out = dict(config)
    knowledge = list(get_knowledge_packages(config))
    # Remove existing entry with same name
    knowledge = [e for e in knowledge if e["name"] != name]
    knowledge.append({"name": name, "source": source, "version": version})
    out["knowledge"] = knowledge
    return out


def remove_knowledge_package_from_config(config: Dict[str, Any], name: str) -> Dict[str, Any]:
    """Return new config with package removed from knowledge list."""
    out = dict(config)
    knowledge = [e for e in get_knowledge_packages(config) if e["name"] != name]
    out["knowledge"] = knowledge
    return out


def normalize_source(source: str) -> str:
    """
    Normalize source string for use in directory name: safe on Windows and Unix.
    Replace ':' and '/' with '-'. Example: github:something/cross-knowledge/commons -> github-something-cross-knowledge-commons.
    """
    return re.sub(r"[:/\\]+", "-", source).strip("-")


def normalize_name_for_dir(name: str) -> str:
    """
    Normalize name for use in directory name: replace / with - so paths like AWS/aws-sqs
    become AWS-aws-sqs (filesystem-safe).
    """
    return re.sub(r"[/\\]+", "-", name).strip("-")


def get_package_dir_name(name: str, source: str) -> str:
    """Directory name under .cliplin/knowledge/ for this package."""
    return f"{normalize_name_for_dir(name)}-{normalize_source(source)}"


def get_knowledge_root(project_root: Path) -> Path:
    """Path to .cliplin/knowledge/."""
    return project_root / ".cliplin" / "knowledge"


def get_package_path(project_root: Path, name: str, source: str) -> Path:
    """Path to the package directory under .cliplin/knowledge/."""
    return get_knowledge_root(project_root) / get_package_dir_name(name, source)


def source_to_git_url(source: str) -> Optional[str]:
    """
    Convert source to Git URL. Supports github:owner/repo or owner/repo (assumes GitHub).
    Returns None if not recognized.
    """
    s = source.strip()
    if s.startswith("github:"):
        rest = s[7:].strip("/")
        return f"https://github.com/{rest}.git"
    if s.startswith("https://") or s.startswith("git@"):
        return s
    # owner/repo style
    if "/" in s and " " not in s:
        return f"https://github.com/{s}.git"
    return None


def _flatten_package_subfolder(pkg_path: Path, name: str) -> None:
    """
    Move contents of pkg_path/name/ to pkg_path/ so the package root holds the
    subfolder content (multi-package repo: name identifies the subfolder).
    Cleans the package root first (except .git and the name subfolder) so that
    a previous flatten (e.g. old adr/) is removed before moving the new content.
    """
    subfolder = pkg_path / name
    if not subfolder.is_dir():
        return
    # Remove any existing content at package root except .git and the subfolder
    # (leftover from a previous flatten, e.g. adr/ after repo renamed to adrs/)
    for item in pkg_path.iterdir():
        if item.name == ".git" or item.name == name:
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()
    for item in subfolder.iterdir():
        dest = pkg_path / item.name
        if dest.exists():
            if dest.is_dir():
                shutil.rmtree(dest)
            else:
                dest.unlink()
        shutil.move(str(item), str(pkg_path))
    subfolder.rmdir()


def _flatten_subpath(pkg_path: Path, subpath: str) -> None:
    """
    Move contents of pkg_path/subpath/ to pkg_path/ so the package root holds the
    subpath content (e.g. name=AWS/aws-sqs means sparse checkout of that path, then flatten).
    Cleans the package root first (except .git and the subpath) before moving.
    """
    subfolder = pkg_path / subpath
    if not subfolder.is_dir():
        return
    # Remove any existing content at package root except .git and the subpath hierarchy
    for item in pkg_path.iterdir():
        if item.name == ".git":
            continue
        if item == subfolder or item in subfolder.parents:
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()
    # Move subpath contents to package root
    for item in subfolder.iterdir():
        dest = pkg_path / item.name
        if dest.exists():
            if dest.is_dir():
                shutil.rmtree(dest)
            else:
                dest.unlink()
        shutil.move(str(item), str(pkg_path))
    # Remove subpath directories (from deepest to root)
    current = subfolder
    while current != pkg_path:
        parent = current.parent
        if current.is_dir() and not any(current.iterdir()):
            current.rmdir()
        current = parent


def clone_package(
    project_root: Path,
    name: str,
    source: str,
    version: str,
) -> Path:
    """
    Clone the repository for the package with sparse checkout into .cliplin/knowledge/<name>-<source_normalized>.
    - Name with subpath (e.g. AWS/aws-sqs): sparse checkout that path, then flatten to package root.
    - Multi-package repo: sparse checkout only <name>/ (top-level) then flatten.
    - Single-package repo: if no top-level <name>/ folder, sparse checkout standard paths (docs/adrs, etc.).
    Returns the path to the package directory.
    """
    pkg_path = get_package_path(project_root, name, source)
    if pkg_path.exists():
        shutil.rmtree(pkg_path)
    get_knowledge_root(project_root).mkdir(parents=True, exist_ok=True)

    url = source_to_git_url(source)
    if not url:
        raise ValueError(f"Unsupported source format: {source}. Use github:owner/repo or a Git URL.")

    # Clone with no checkout to avoid downloading everything
    subprocess.run(
        ["git", "clone", "--filter=blob:none", "--no-checkout", url, str(pkg_path)],
        check=True,
        capture_output=True,
        text=True,
        cwd=project_root,
    )
    subprocess.run(
        ["git", "-C", str(pkg_path), "sparse-checkout", "init", "--no-cone"],
        check=True,
        capture_output=True,
        text=True,
    )

    if "/" in name or "\\" in name:
        # Name is a subpath (e.g. AWS/aws-sqs): sparse checkout that path, then flatten
        subprocess.run(
            ["git", "-C", str(pkg_path), "sparse-checkout", "set", name],
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            ["git", "-C", str(pkg_path), "checkout", version],
            check=True,
            capture_output=True,
            text=True,
        )
        _flatten_subpath(pkg_path, name)
    else:
        # Name is top-level: try multi-package layout first
        subprocess.run(
            ["git", "-C", str(pkg_path), "sparse-checkout", "set", name],
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            ["git", "-C", str(pkg_path), "checkout", version],
            check=True,
            capture_output=True,
            text=True,
        )
        name_dir = pkg_path / name
        if name_dir.is_dir() and any(name_dir.iterdir()):
            _flatten_package_subfolder(pkg_path, name)
        else:
            # Single-package repo: no top-level name folder; materialize root-level context paths
            if name_dir.exists():
                shutil.rmtree(name_dir)
            subprocess.run(
                ["git", "-C", str(pkg_path), "sparse-checkout", "set"] + SPARSE_PATHS,
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "-C", str(pkg_path), "checkout", version],
                check=True,
                capture_output=True,
                text=True,
            )
    return pkg_path


def update_package_checkout(project_root: Path, name: str, source: str, version: str) -> Path:
    """Fetch and checkout the given version in the existing package directory. Re-flatten if multi-package or subpath layout."""
    pkg_path = get_package_path(project_root, name, source)
    if not pkg_path.exists():
        raise FileNotFoundError(f"Package directory not found: {pkg_path}")
    subprocess.run(
        ["git", "-C", str(pkg_path), "fetch", "origin", version],
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "-C", str(pkg_path), "checkout", version],
        check=True,
        capture_output=True,
        text=True,
    )
    if "/" in name or "\\" in name:
        _flatten_subpath(pkg_path, name)
    else:
        name_dir = pkg_path / name
        if name_dir.is_dir() and any(name_dir.iterdir()):
            _flatten_package_subfolder(pkg_path, name)
    return pkg_path


def remove_package_directory(project_root: Path, name: str, source: str) -> None:
    """Remove the package directory under .cliplin/knowledge/."""
    pkg_path = get_package_path(project_root, name, source)
    if pkg_path.exists():
        shutil.rmtree(pkg_path)


def find_package_by_name(
    project_root: Path, name: str
) -> Optional[Dict[str, str]]:
    """
    Find a knowledge package by name: first in config, then by matching installed directory.
    Returns dict with name, source, version (version may be empty if only found on disk).
    """
    config = load_config(project_root)
    for pkg in get_knowledge_packages(config):
        if pkg["name"] == name:
            return pkg
    # Check installed dirs: .cliplin/knowledge/<name>-*
    knowledge_root = get_knowledge_root(project_root)
    if not knowledge_root.exists():
        return None
    dir_prefix = normalize_name_for_dir(name) + "-"
    for d in knowledge_root.iterdir():
        if d.is_dir() and d.name.startswith(dir_prefix):
            # Recover source from dir name: name-source_normalized -> source is lost, we only have normalized
            # So we cannot recover exact source from disk. Require config for remove/update when we need source.
            return None
    return None
