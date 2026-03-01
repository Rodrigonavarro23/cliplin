"""Validate command for checking Cliplin project structure."""

import sys
from pathlib import Path
from typing import Any, Dict, Optional

import typer
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from cliplin.utils.chromadb import (
    REQUIRED_COLLECTIONS,
    get_chromadb_client,
    get_chromadb_path,
    verify_collections,
)
from cliplin.utils.ai_host_integrations import get_integration, get_known_ai_tool_ids

console = Console()

REQUIRED_DIRS = [
    "docs/adrs",
    "docs/business",
    "docs/features",
    "docs/tdrs",
    "docs/ui-intent",
    ".cliplin/data/context",
]


def validate_command() -> None:
    """Validate the Cliplin project structure and configuration."""
    project_root = Path.cwd()
    
    console.print(Panel.fit("[bold cyan]Validating Cliplin Project[/bold cyan]"))
    
    errors = []
    warnings = []
    
    # Check if Cliplin is initialized
    if not is_cliplin_initialized(project_root):
        console.print("[bold red]Error:[/bold red] Cliplin is not initialized in this directory.")
        console.print("Run 'cliplin init' to initialize the project.")
        raise typer.Exit(code=1)
    
    # Validate directories
    console.print("\n[bold]Checking directories...[/bold]")
    for dir_path in REQUIRED_DIRS:
        full_path = project_root / dir_path
        if full_path.exists():
            console.print(f"  [green]✓[/green] {dir_path}/")
        else:
            console.print(f"  [red]✗[/red] {dir_path}/ (missing)")
            errors.append(f"Missing directory: {dir_path}")
    
    # Validate ChromaDB
    console.print("\n[bold]Checking ChromaDB...[/bold]")
    db_path = get_chromadb_path(project_root)
    if db_path.exists():
        console.print(f"  [green]✓[/green] ChromaDB database exists at {db_path.relative_to(project_root)}")
        
        # Check collections
        try:
            client = get_chromadb_client(project_root)
            missing_collections = verify_collections(client)
            
            if missing_collections:
                for col in missing_collections:
                    console.print(f"  [red]✗[/red] Collection '{col}' is missing")
                    errors.append(f"Missing ChromaDB collection: {col}")
            else:
                for col in REQUIRED_COLLECTIONS:
                    console.print(f"  [green]✓[/green] Collection '{col}' exists")
        except Exception as e:
            console.print(f"  [red]✗[/red] Failed to access ChromaDB: {e}")
            errors.append(f"ChromaDB access error: {e}")
    else:
        console.print(f"  [red]✗[/red] ChromaDB database not found at {db_path.relative_to(project_root)}")
        errors.append("ChromaDB database not found")
    
    # Validate Python version
    console.print("\n[bold]Checking Python version...[/bold]")
    if sys.version_info >= (3, 10):
        console.print(f"  [green]✓[/green] Python {sys.version.split()[0]} (>= 3.10 required)")
    else:
        console.print(
            f"  [red]✗[/red] Python {sys.version.split()[0]} (3.10+ required)"
        )
        errors.append("Python version too old")
    
    # Check for configuration files and MCP file for configured AI tool
    console.print("\n[bold]Checking configuration files...[/bold]")
    config_file = project_root / "cliplin.yaml"
    if config_file.exists():
        console.print(f"  [green]✓[/green] Config file exists")
        ai_tool: Optional[str] = _get_ai_tool_from_config(config_file)
        if ai_tool is not None and get_integration(ai_tool) is not None:
            integration = get_integration(ai_tool)
            mcp_path = integration.mcp_config_path if integration else None
            if mcp_path:
                mcp_file = project_root / mcp_path
                if mcp_file.exists():
                    console.print(f"  [green]✓[/green] MCP config for {ai_tool!r} exists at {mcp_path}")
                else:
                    console.print(f"  [red]✗[/red] MCP config for {ai_tool!r} not found at {mcp_path}")
                    errors.append(f"Missing MCP config file for ai_tool {ai_tool!r}: {mcp_path}")
        elif ai_tool is not None and get_integration(ai_tool) is None:
            console.print(f"  [yellow]⚠[/yellow]  Unknown ai_tool in config: {ai_tool!r}")
            warnings.append(f"Unknown ai_tool in config: {ai_tool!r}")
    else:
        console.print(f"  [yellow]⚠[/yellow]  Config file not found (optional)")
        warnings.append("Config file not found")

    # Summary
    console.print("\n" + "=" * 50)
    if errors:
        console.print(Panel.fit(
            f"[bold red]Validation Failed[/bold red]\n\n"
            f"Found {len(errors)} error(s) and {len(warnings)} warning(s).\n\n"
            "Errors:\n" + "\n".join(f"  • {e}" for e in errors),
            border_style="red",
        ))
        raise typer.Exit(code=1)
    else:
        console.print(Panel.fit(
            "[bold green]✓ Validation Passed[/bold green]\n\n"
            f"All checks passed. {len(warnings)} warning(s).",
            border_style="green",
        ))


def _get_ai_tool_from_config(config_path: Path) -> Optional[str]:
    """Read ai_tool from cliplin.yaml at project root if present."""
    if not config_path.exists():
        return None
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data: Dict[str, Any] = yaml.safe_load(f) or {}
        return data.get("ai_tool")
    except (yaml.YAMLError, IOError):
        return None


def is_cliplin_initialized(project_root: Path) -> bool:
    """Check if Cliplin is already initialized in the project."""
    cliplin_dir = project_root / ".cliplin"
    return cliplin_dir.exists() and (cliplin_dir / "data" / "context").exists()

