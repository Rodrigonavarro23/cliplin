---
tdr: "1.0"
id: "cliplin-cli-stack"
title: "Cliplin CLI Technical Stack"
summary: "Technical stack and package configuration for the Cliplin CLI tool, installable via uv."
---

# rules

CLI must be implemented in Python 3.10+ with type hints

Package management must use `uv` (Astral UV) as the primary installer and dependency manager

Project structure must follow Python packaging standards with `pyproject.toml` for uv compatibility

CLI entry point must be accessible via `cliplin` command after installation

All commands must use `typer` or `click` for CLI argument parsing and subcommands

CLI must be executable as a module: `python -m cliplin` or standalone: `cliplin`

CLI must validate Python version compatibility (>=3.10) before installation

## Package dependencies must include

- Python >= 3.10
- uv (Astral UV) >= 0.1.0
- typer >= 0.9.0 (or click >= 8.0.0)
- pyyaml >= 6.0
- rich >= 13.0.0 (for terminal output formatting)
- pydantic >= 2.0.0 (for configuration validation)

## Project structure must include

- src/cliplin/__init__.py (main package)
- src/cliplin/cli.py (CLI entry point and command registration)
- pyproject.toml (package configuration for uv with PEP 621 format)
- README.md (project documentation)

## Package installation methods must support

- uv pip install: via `uv pip install cliplin` (requires uv in PATH)
- uv tool install: via `uv tool install cliplin` or `uvx cliplin` for one-time execution
- development install: via `uv pip install -e .` or `uv sync` if using uv project structure

## pyproject.toml must

- Use PEP 621 standard for package metadata and dependencies
- Define entry points in `[project.scripts]` with `cliplin = cliplin.cli:main`
- Specify dependencies in `[project.dependencies]`
- Specify Python version requirement as `requires-python = \">=3.10\"`
- Include build system `[build-system]` with `requires = [\"hatchling\"]` or compatible

## CLI command organization must follow

- Each command in separate module under `src/cliplin/commands/`
- Commands registered in `src/cliplin/cli.py` using `app.command(name="command")(command_function)`
- Utility functions in `src/cliplin/utils/` for shared functionality
- Commands should validate prerequisites early and provide clear error messages

## Rich library usage rules

- Never concatenate Rich objects (Panel, Table) with strings using `+` operator
- Use separate `console.print()` calls for Rich objects
- Build text content as strings first, then pass to Rich constructors
- Example: `console.print()` then `console.print(Panel.fit(text))` not `console.print("\n" + Panel.fit(text))`

## Init and version control

- When running `cliplin init`, the CLI MUST ensure the `.cliplin` directory is ignored by Git.
- If `.gitignore` exists in the project root, append `.cliplin` (or ensure a line containing `.cliplin` is present) if not already present; use UTF-8 encoding for read/write.
- If `.gitignore` does not exist, create it at project root with a single line `.cliplin`.
- Do not remove or reorder other lines in `.gitignore`; only add or ensure the `.cliplin` entry.

## Template directory discovery

- Search in order: package_dir/template, project_root/template, cwd/template, ~/.cliplin/template
- Template directory must contain required structure for project initialization
- Template files are copied and adjusted based on AI tool selection

## ChromaDB integration patterns

- Use `chromadb.PersistentClient` with path to `.cliplin/data/context/`
- ALWAYS resolve paths to absolute using `.resolve()` before passing to ChromaDB (critical for Windows)
- Initialize collections using `get_or_create_collection()` to avoid errors
- Use file path (relative to project root) as document ID
- Include metadata: file_path, type, collection for all indexed documents
- Check for existing documents before adding to avoid duplicates
- Wrap client initialization in try-except with path logging for debugging

## File operations and encoding (CRITICAL for cross-platform compatibility)

- ALWAYS specify `encoding="utf-8"` in ALL file write/read operations
- This applies to: `write_text()`, `read_text()`, and any file I/O
- Default encoding varies by platform (Windows uses cp1252, Linux/macOS use UTF-8)
- See `docs/tdrs/windows-compatibility-file-operations.md` for detailed rules

## Development and testing

- Use `uv pip install -e .` for development mode installation
- Activate virtual environment before testing: `source .venv/bin/activate`
- Reinstall after code changes: `uv pip install -e . --force-reinstall`
- Test in isolated directories to avoid affecting main project

## Error handling

- Validate Python version at CLI entry point (main callback)
- Use `typer.Exit(code=1)` for error conditions
- Use Rich console for formatted error messages
- Provide clear, actionable error messages to users
code_refs:
  - "pyproject.toml"
  - "src/cliplin/__init__.py"
  - "src/cliplin/cli.py"
  - "src/cliplin/commands/"
  - "src/cliplin/utils/"
  - "docs/adrs/001-cli-implementation-patterns.md"
  - "docs/tdrs/windows-compatibility-file-operations.md"
