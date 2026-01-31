"""Reindex command for updating context store. Depends on ContextStore and FingerprintStore protocols."""

from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from cliplin.protocols import ContextStore, FingerprintStore
from cliplin.utils.chromadb import (
    COLLECTION_MAPPINGS,
    get_collection_for_file,
    get_context_store,
    get_file_type,
)
from cliplin.utils.fingerprint import get_fingerprint_store

console = Console()


def reindex_command(
    file_path: Optional[str] = typer.Argument(
        None,
        help="Specific file path to reindex (relative to project root)",
    ),
    type: Optional[str] = typer.Option(
        None,
        "--type",
        help="Reindex files of a specific type (ts4, feature, md, yaml)",
    ),
    directory: Optional[str] = typer.Option(
        None,
        "--directory",
        help="Reindex all files in a specific directory",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Review changes without reindexing",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        help="Display detailed output",
    ),
    interactive: bool = typer.Option(
        False,
        "--interactive",
        help="Prompt for confirmation before reindexing",
    ),
) -> None:
    """Reindex context files into the context store (protocol-based)."""
    project_root = Path.cwd()
    store: ContextStore = get_context_store(project_root)
    fingerprint_store: FingerprintStore = get_fingerprint_store(project_root)

    if not store.is_initialized():
        console.print(
            "[bold red]Error:[/bold red] Context store is not initialized.\n"
            "Run 'cliplin init' to initialize the project first."
        )
        raise typer.Exit(code=1)

    try:
        missing_collections = store.ensure_collections()
        if missing_collections:
            console.print("[bold]Creating missing collections...[/bold]")
            for col_name in missing_collections:
                console.print(f"  [green]✓[/green] Created collection '{col_name}'")

        files_to_process = get_files_to_reindex(
            project_root, file_path, type, directory
        )

        if not files_to_process:
            console.print("[yellow]No files found to reindex.[/yellow]")
            raise typer.Exit()

        if dry_run:
            console.print(Panel.fit("[bold cyan]Dry Run Mode[/bold cyan]"))
            display_dry_run_report(store, fingerprint_store, files_to_process, project_root)
            raise typer.Exit()

        if interactive:
            console.print(f"\n[bold]Files to reindex:[/bold] {len(files_to_process)}")
            for f in files_to_process[:10]:
                console.print(f"  • {f.relative_to(project_root)}")
            if len(files_to_process) > 10:
                console.print(f"  ... and {len(files_to_process) - 10} more")

            if not typer.confirm("\nReindex these files?"):
                console.print("[yellow]Aborted.[/yellow]")
                raise typer.Exit()

        console.print(Panel.fit("[bold cyan]Reindexing Context Files[/bold cyan]"))

        stats = {"added": 0, "updated": 0, "skipped": 0, "errors": 0}

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Reindexing...", total=len(files_to_process))
            for file_path_obj in files_to_process:
                try:
                    result = reindex_file(
                        store, fingerprint_store, file_path_obj, project_root, verbose
                    )
                    stats[result] += 1
                    progress.update(task, advance=1)
                except Exception as e:
                    stats["errors"] += 1
                    if verbose:
                        console.print(f"  [red]✗[/red] Error processing {file_path_obj}: {e}")
                    progress.update(task, advance=1)

        display_summary(stats)

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)


def get_files_to_reindex(
    project_root: Path,
    file_path: Optional[str],
    file_type: Optional[str],
    directory: Optional[str],
) -> List[Path]:
    """Get list of files to reindex based on arguments."""
    files = []
    
    if file_path:
        # Single file
        full_path = project_root / file_path
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Validate it's in a context directory
        collection = get_collection_for_file(full_path, project_root)
        if not collection:
            raise ValueError(
                f"File is not in a valid context directory: {file_path}\n"
                "Valid directories: docs/adrs, docs/business, docs/features, docs/ts4, docs/ui-intent"
            )
        
        files.append(full_path)
    
    elif file_type:
        # Files of specific type
        type_mapping = {
            "ts4": ("docs/ts4", "*.ts4"),
            "feature": ("docs/features", "*.feature"),
            "md": ("docs/adrs", "*.md"),  # Could be adrs or business
            "yaml": ("docs/ui-intent", "*.yaml"),
        }
        
        if file_type not in type_mapping:
            raise ValueError(
                f"Unknown file type: {file_type}\n"
                f"Valid types: {', '.join(type_mapping.keys())}"
            )
        
        dir_pattern = type_mapping[file_type]
        if file_type == "md":
            # Search both adrs and business
            for dir_name in ["docs/adrs", "docs/business"]:
                dir_path = project_root / dir_name
                if dir_path.exists():
                    files.extend(dir_path.rglob("*.md"))
        else:
            dir_path = project_root / dir_pattern[0]
            if dir_path.exists():
                files.extend(dir_path.rglob(dir_pattern[1]))
    
    elif directory:
        # Files in specific directory
        dir_path = project_root / directory
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        # Determine file pattern based on directory
        for collection_name, mapping in COLLECTION_MAPPINGS.items():
            if directory in mapping["directories"]:
                files.extend(dir_path.rglob(mapping["file_pattern"]))
                break
        else:
            raise ValueError(f"Directory is not a valid context directory: {directory}")
    
    else:
        # All context files
        for collection_name, mapping in COLLECTION_MAPPINGS.items():
            for dir_name in mapping["directories"]:
                dir_path = project_root / dir_name
                if dir_path.exists():
                    files.extend(dir_path.rglob(mapping["file_pattern"]))
    
    return sorted(set(files))


def reindex_file(
    store: ContextStore,
    fingerprint_store: FingerprintStore,
    file_path: Path,
    project_root: Path,
    verbose: bool,
) -> str:
    """Reindex a single file. Returns 'added', 'updated', or 'skipped' (unchanged)."""
    relative_path = file_path.relative_to(project_root)
    file_id = str(relative_path)

    collection_name = get_collection_for_file(file_path, project_root)
    if not collection_name:
        raise ValueError(f"Cannot determine collection for {relative_path}")

    file_type = get_file_type(file_path, project_root)
    if not file_type:
        raise ValueError(f"Cannot determine file type for {relative_path}")

    # Skip if file has not changed (fingerprint matches stored)
    changed_result = fingerprint_store.has_changed(file_id, file_system_path=file_path)
    if not changed_result["changed"] and changed_result.get("stored_fingerprint") is not None:
        if verbose:
            console.print(f"  [dim]○[/dim] Unchanged {relative_path}")
        return "skipped"

    content = file_path.read_text(encoding="utf-8")
    content_bytes = content.encode("utf-8")
    metadata = {
        "file_path": file_id,
        "type": file_type,
        "collection": collection_name,
    }

    exists = store.document_exists(collection_name, file_id)

    if exists:
        store.update_documents(
            collection_name, [file_id], documents=[content], metadatas=[metadata]
        )
        fingerprint_store.update(file_id, content_bytes)
        if verbose:
            console.print(f"  [yellow]↻[/yellow] Updated {relative_path}")
        return "updated"
    else:
        store.add_documents(
            collection_name, [file_id], [content], metadatas=[metadata]
        )
        fingerprint_store.update(file_id, content_bytes)
        if verbose:
            console.print(f"  [green]+[/green] Added {relative_path}")
        return "added"


def display_dry_run_report(
    store: ContextStore,
    fingerprint_store: FingerprintStore,
    files: List[Path],
    project_root: Path,
) -> None:
    """Display a dry-run report: which files would be added, updated, or skipped (unchanged)."""
    table = Table(title="Files to Reindex")
    table.add_column("File Path", style="cyan")
    table.add_column("Status", style="magenta")
    table.add_column("Action", style="green")

    for file_path in files:
        relative_path = file_path.relative_to(project_root)
        file_id = str(relative_path)

        collection_name = get_collection_for_file(file_path, project_root)
        if not collection_name:
            table.add_row(str(relative_path), "Invalid", "Skip")
            continue

        try:
            changed_result = fingerprint_store.has_changed(file_id, file_system_path=file_path)
            if not changed_result["changed"] and changed_result.get("stored_fingerprint") is not None:
                table.add_row(str(relative_path), "Unchanged", "Skip")
                continue
            if store.document_exists(collection_name, file_id):
                table.add_row(str(relative_path), "Changed", "Update")
            else:
                table.add_row(str(relative_path), "New", "Add")
        except Exception:
            table.add_row(str(relative_path), "New", "Add")

    console.print(table)


def display_summary(stats: dict) -> None:
    """Display reindexing summary."""
    table = Table(title="Reindexing Summary")
    table.add_column("Action", style="cyan")
    table.add_column("Count", style="magenta")
    
    table.add_row("Files Added", str(stats["added"]))
    table.add_row("Files Updated", str(stats["updated"]))
    table.add_row("Files Skipped", str(stats["skipped"]))
    if stats["errors"] > 0:
        table.add_row("Errors", f"[red]{stats['errors']}[/red]")
    
    console.print()
    console.print(table)
    
    if stats["errors"] == 0:
        console.print(
            Panel.fit(
                "[bold green]✓ Reindexing completed successfully![/bold green]",
                border_style="green",
            )
        )
    else:
        console.print(
            Panel.fit(
                f"[bold yellow]⚠ Reindexing completed with {stats['errors']} error(s)[/bold yellow]",
                border_style="yellow",
            )
        )

