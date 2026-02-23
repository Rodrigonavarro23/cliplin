---
tdr: "1.0"
id: "windows-compatibility-file-operations"
title: "Windows Compatibility: File Operations and Encoding"
summary: "Critical rules for file operations, encoding handling, and path management to ensure cross-platform compatibility, especially for Windows environments."
---

# rules

## ALWAYS specify encoding explicitly for all file write operations

- Use `encoding="utf-8"` parameter in all `write_text()`, `write_bytes()`, and file write operations
- Default encoding varies by platform (Windows may use cp1252 or other local encoding)
- Example: `file_path.write_text(content, encoding="utf-8")` NOT `file_path.write_text(content)`
- This applies to: text files, templates, configuration files, markdown, YAML, JSON, and any text-based files

## ALWAYS specify encoding explicitly for all file read operations

- Use `encoding="utf-8"` parameter in all `read_text()` operations
- Ensure consistency between read and write operations
- Example: `file_path.read_text(encoding="utf-8")`

## Path handling for cross-platform compatibility

- Use `pathlib.Path` objects instead of string paths when possible
- Always resolve paths to absolute using `.resolve()` before passing to external libraries
- Example: `absolute_path = db_path.parent.resolve()` before passing to ChromaDB
- This is critical for Windows compatibility with libraries like ChromaDB that require absolute paths

## Path operations for database and external services

- Convert `Path` objects to strings using `str(path)` when passing to external libraries
- Ensure paths are absolute and resolved before database operations
- Use `Path.resolve()` to normalize paths and handle Windows path quirks
- Never rely on relative paths for persistent storage operations

## Error handling for file operations

- Wrap file operations in try-except blocks with informative error messages
- Include path information in error messages for debugging
- Log the absolute path when file operations fail
- Example:
  ```
  try:
      file_path.write_text(content, encoding="utf-8")
  except Exception as e:
      console.print(f"Error writing file: {e}")
      console.print(f"Path: {file_path.resolve()}")
      raise
  ```

## Windows-specific considerations

- Windows may have issues with long paths (>260 characters) - use absolute resolved paths
- Windows uses different line endings (CRLF vs LF) - Python handles this automatically with text mode and UTF-8
- Windows may have permission issues with certain directories - ensure proper directory creation with `mkdir(parents=True, exist_ok=True)`
- Windows path separators are handled automatically by `pathlib.Path`, but always use forward slashes in string literals or `Path` objects

## Template file creation

- ALL template generation functions MUST use `encoding="utf-8"` when writing files
- This includes: README files, ADR files, configuration files, rule files, and any generated content
- Templates often contain special characters, Unicode, and multilingual content
- Encoding errors in templates cause silent failures or corrupted files

## Database client initialization (ChromaDB, SQLite, etc.)

- Always resolve database paths to absolute before passing to client
- Use `path.resolve()` to handle Windows path normalization
- Wrap client initialization in try-except with path logging
- Example:
  ```
  absolute_path = db_path.parent.resolve()
  client = chromadb.PersistentClient(path=str(absolute_path))
  ```

## Testing cross-platform compatibility

- Test file operations on Windows, macOS, and Linux if possible
- Test with paths containing spaces, special characters, and non-ASCII characters
- Test with long paths on Windows
- Verify UTF-8 encoding preservation across platforms

## Code review checklist

- [ ] All `write_text()` calls specify `encoding="utf-8"`
- [ ] All `read_text()` calls specify `encoding="utf-8"`
- [ ] All database/external library paths are resolved to absolute
- [ ] Path objects converted to strings with `str()` for external libraries
- [ ] Error handling includes path information in messages
- [ ] Directory creation uses `mkdir(parents=True, exist_ok=True)`
code_refs:
  - "src/cliplin/utils/templates.py"
  - "src/cliplin/utils/chromadb.py"
  - "src/cliplin/commands/reindex.py"
  - "docs/adrs/001-cli-implementation-patterns.md"
