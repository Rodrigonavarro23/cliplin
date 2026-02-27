"""Init command for initializing Cliplin projects."""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from cliplin.utils.chromadb import (
    get_chromadb_client,
    get_context_store,
    initialize_collections,
)
from cliplin.utils.fingerprint import get_fingerprint_store
from cliplin.utils.ai_host_integrations import (
    create_ai_tool_config,
    get_known_ai_tool_ids,
)
from cliplin.utils.templates import (
    FRAMEWORK_PACKAGE_DIR,
    create_cliplin_config,
    create_framework_knowledge_package,
    create_readme_file,
)
from cliplin.commands.reindex import get_files_to_reindex, reindex_file
from cliplin.commands.knowledge import knowledge_install_command

console = Console()

# Required directory structure (TDR is default; docs/ts4 is deprecated but still supported if present)
REQUIRED_DIRS = [
    "docs/adrs",
    "docs/business",
    "docs/features",
    "docs/tdrs",
    "docs/ui-intent",
    ".cliplin/data/context",
]


def init_command(
    ai: Optional[str] = typer.Option(
        None,
        "--ai",
        help="AI tool ID (cursor, claude-desktop, gemini, etc.)",
    ),
) -> None:
    """Initialize a new Cliplin project in the current directory."""
    project_root = Path.cwd()
    was_already_initialized = is_cliplin_initialized(project_root)

    # Check if already initialized
    if was_already_initialized:
        console.print(
            "[yellow]⚠[/yellow]  Cliplin appears to be already initialized in this directory."
        )
        if not typer.confirm("Do you want to continue anyway?"):
            console.print("[yellow]Aborted.[/yellow]")
            raise typer.Exit()

    console.print(Panel.fit("[bold cyan]Initializing Cliplin Project[/bold cyan]"))
    
    # Validate Python version
    if sys.version_info < (3, 10):
        console.print(
            "[bold red]Error:[/bold red] Python 3.10 or higher is required. "
            f"Current version: {sys.version.split()[0]}"
        )
        raise typer.Exit(code=1)
    
    try:
        # Create directory structure
        console.print("\n[bold]Creating directory structure...[/bold]")
        create_directory_structure(project_root)
        ensure_cliplin_in_gitignore(project_root)

        # Create configuration files
        console.print("\n[bold]Creating configuration files...[/bold]")
        create_readme_file(project_root)
        create_cliplin_config(project_root, ai)
        
        # Create/update built-in framework package in .cliplin/knowledge/cliplin-framework
        console.print("\n[bold]Creating framework context documentation...[/bold]")
        create_framework_knowledge_package(project_root)
        
        # Create AI tool configuration if specified
        if ai:
            if ai not in get_known_ai_tool_ids():
                console.print(
                    f"[bold red]Error:[/bold red] Unknown AI tool: {ai}\n"
                    f"Available tools: {', '.join(get_known_ai_tool_ids())}"
                )
                raise typer.Exit(code=1)
            
            console.print(f"\n[bold]Configuring for AI tool: {ai}...[/bold]")
            create_ai_tool_config(project_root, ai)
        
        # Initialize ChromaDB
        console.print("\n[bold]Initializing ChromaDB...[/bold]")
        client = get_chromadb_client(project_root)
        initialize_collections(client)
        
        # Validate project structure
        console.print("\n[bold]Validating project structure...[/bold]")
        validate_project_structure(project_root)
        
        # Index framework package automatically
        console.print("\n[bold]Indexing framework context...[/bold]")
        _reindex_framework_package(project_root)

        # On re-init, reinstall knowledge packages from config
        if was_already_initialized:
            console.print("\n[bold]Installing knowledge packages from config...[/bold]")
            knowledge_install_command(force=False)

        # Success message
        success_text = (
            "[bold green]✓ Cliplin project initialized successfully![/bold green]\n\n"
            f"Project root: [cyan]{project_root}[/cyan]\n"
        )
        if ai:
            success_text += f"AI tool: [cyan]{ai}[/cyan]\n"
        success_text += (
            "\nNext steps:\n"
            "  - Add your feature files to docs/features/\n"
            "  - Add your TDR specs to docs/tdrs/ (Technical Decision Records)\n"
            "  - Run 'cliplin reindex' to index new context files"
        )
        if (project_root / "docs" / "ts4").exists():
            success_text += (
                "\n\n[yellow]Note:[/yellow] You have docs/ts4/. TS4 is deprecated; consider migrating to TDR (docs/tdrs/). Format: framework ADR 003-tdr-format (in .cliplin/knowledge/cliplin-framework/docs/adrs/)."
            )
        console.print()
        console.print(Panel.fit(success_text, border_style="green"))
        
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)


def is_cliplin_initialized(project_root: Path) -> bool:
    """Check if Cliplin is already initialized in the project."""
    cliplin_dir = project_root / ".cliplin"
    return cliplin_dir.exists() and (cliplin_dir / "data" / "context").exists()


def ensure_cliplin_in_gitignore(project_root: Path) -> None:
    """Ensure .cliplin is listed in .gitignore (create or append); use UTF-8. Does not remove or reorder other lines."""
    gitignore_path = project_root / ".gitignore"
    entry = ".cliplin"
    if not gitignore_path.exists():
        gitignore_path.write_text(entry + "\n", encoding="utf-8")
        console.print(f"  [green]✓[/green] Created .gitignore with {entry}")
        return
    content = gitignore_path.read_text(encoding="utf-8")
    if any(entry in line for line in content.splitlines()):
        return
    new_content = content.rstrip("\n") + ("\n" if content else "") + entry + "\n"
    gitignore_path.write_text(new_content, encoding="utf-8")
    console.print(f"  [green]✓[/green] Added {entry} to .gitignore")


def create_directory_structure(project_root: Path) -> None:
    """Create the required Cliplin directory structure."""
    for dir_path in REQUIRED_DIRS:
        full_path = project_root / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        console.print(f"  [green]✓[/green] Created {dir_path}/")


def validate_project_structure(project_root: Path) -> None:
    """Validate that all required directories exist."""
    missing = []
    for dir_path in REQUIRED_DIRS:
        if not (project_root / dir_path).exists():
            missing.append(dir_path)
    
    if missing:
        console.print(f"  [red]✗[/red] Missing directories: {', '.join(missing)}")
        raise ValueError("Project structure validation failed")
    
    console.print("  [green]✓[/green] All required directories exist")


def _reindex_framework_package(project_root: Path) -> None:
    """Index the built-in framework package into the context store."""
    store = get_context_store(project_root)
    fingerprint_store = get_fingerprint_store(project_root)
    store.ensure_collections()
    framework_dir = f".cliplin/knowledge/{FRAMEWORK_PACKAGE_DIR}"
    try:
        files = get_files_to_reindex(
            project_root,
            file_path=None,
            file_type=None,
            directory=framework_dir,
        )
        for f in files:
            try:
                reindex_file(store, fingerprint_store, f, project_root, verbose=False)
            except Exception:
                pass
        if files:
            console.print(f"  [green]✓[/green] Indexed {len(files)} framework document(s)")
    except FileNotFoundError:
        pass  # Framework dir may not exist in edge cases

