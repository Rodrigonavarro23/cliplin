---
tdr: "1.0"
id: "knowledge-packages"
title: "Knowledge Packages and cliplin knowledge Command"
summary: "Config schema for knowledge in cliplin.yaml, installation layout under .cliplin/knowledge/, use of git sparse checkout, and CLI subcommands list, add, remove, update, show, install."
---

# rules

## cliplin.yaml — knowledge section (MUST)

- Top-level key `knowledge` is optional; value is a list of package entries
- Each entry: `name` (string), `source` (string), `version` (string). No extra required fields for minimal support
- `name` MAY contain a subpath (e.g. `AWS/aws-sqs`) to install a nested subfolder; the path is used for sparse checkout and flattened to the package root. For filesystem-safe directory names, `/` in name is normalized to `-` (e.g. `AWS-aws-sqs-github-org-repo`)
- `source` format: at least `github:owner/repo`; other backends (e.g. git URL) may be added later and MUST be documented in this TS4
- `version`: branch name, commit SHA, or version tag; used when cloning or updating (e.g. git checkout <version>)
- The CLI command `cliplin knowledge` reads and writes this section; add/remove/update MUST keep the file valid YAML and preserve other top-level keys

## Installation directory (MUST)

- All packages live under `.cliplin/knowledge/` (project root relative)
- Per-package directory name: `<name_normalized>-<source_normalized>`. Normalize `name` for filesystem: replace `/` and `\` by `-` (e.g. `AWS/aws-sqs` → `AWS-aws-sqs`). Normalize `source`: replace `:` and `/` by `-`. Result MUST be unique per (name, source) and valid on Windows and Unix. Example: name=AWS/aws-sqs, source=github:org/repo → `.cliplin/knowledge/AWS-aws-sqs-github-org-repo`
- One directory per package; overwrite or replace on re-install/update
- **Built-in framework package**: `cliplin init` creates `.cliplin/knowledge/cliplin-framework/` with framework ADRs (000, 001, 002, 005). This package is hidden: NOT in cliplin.yaml, NOT listed by `cliplin knowledge list`, updated on every init. Reindex indexes it like any other knowledge package.

## Git sparse checkout (MUST for git-based sources)

- For `source` that resolves to a Git repository, use git sparse checkout so only the desired content is materialized
- **Name with subpath** (e.g. `AWS/aws-sqs`): Sparse checkout SHALL be set to [name] (the path). After checkout, the content at repo/<name>/ SHALL be flattened to the package root: move repo/<name>/* to the package root so the layout is .cliplin/knowledge/<name_normalized>-<source_normalized>/docs/adrs, etc.
- **Multi-package repo** (name without slash): When the repo has multiple packages as top-level folders (e.g. aws/, commons/), the package **name** identifies the subfolder. Sparse checkout SHALL be set to [name] first (only that subfolder). After checkout, flatten as above.
- **Single-package repo**: If the repo has no top-level folder matching the name (root has docs/, ts4/, etc.), sparse checkout SHALL use the standard context paths (docs/adrs, docs/business, docs/features, docs/ts4, docs/ui-intent, rules, skills, templates, and without docs/ prefix) so the root of the clone is the package root
- Use shallow clone where appropriate (e.g. depth 1 for a branch or tag) to reduce size; for a specific commit, ensure that commit is fetched
- Do not rely on `git add --sparse` for the initial clone; that command is for staging. Sparse checkout is configured before or during checkout so the working tree only contains the desired paths

## CLI command and subcommands (MUST)

- Command: `cliplin knowledge`. Subcommands: `list`, `add`, `remove`, `update`, `show`, `install`
- `list`: List packages declared in cliplin.yaml and/or installed under .cliplin/knowledge/; output SHOULD show name, source, version, and installed status/path
- `add`: Add a package (name, source, version); update cliplin.yaml; clone into .cliplin/knowledge/<name>-<source_normalized>; trigger reindex for that package; if host integration supports skills, link skills (see claude-desktop-integration or knowledge-reindex-context for skills)
- `remove`: Remove package from cliplin.yaml; delete its directory under .cliplin/knowledge/; remove its documents from the context store and update fingerprint store; remove skill links if any
- `update`: Update package to specified version (or latest for the configured ref); update clone and cliplin.yaml if version changed; trigger reindex for that package
- `show`: Show details for a package (name, source, version, install path, optionally summary of indexed files or collection counts)
- `install`: Install all packages declared in cliplin.yaml. Without --force: add if not installed, update if installed. With --force: remove directory (and purge context/fingerprint/skills) if exists, then clone fresh using the version in cliplin.yaml; does NOT change version in config; packages not previously installed are installed for the first time
- All subcommands that modify state (add, remove, update, install) MUST run in a project that has cliplin.yaml (or create it with only knowledge if acceptable per product decision); MUST fail clearly if project root or config is missing

## Module layout

- Implement command in `src/cliplin/commands/knowledge.py`; register in `src/cliplin/cli.py` as the `knowledge` command group
- Shared logic: config read/write (cliplin.yaml), path resolution (.cliplin/knowledge), source normalization, and git operations SHOULD live in utils (e.g. a dedicated knowledge or packages module) so that the command only orchestrates; reindex and context store updates use existing utils (chromadb, fingerprint, collection mappings)
code_refs:
  - "src/cliplin/cli.py"
  - "src/cliplin/commands/knowledge.py"
  - "docs/adrs/005-knowledge-packages.md"
  - "docs/tdrs/knowledge-reindex-context.md"
  - "docs/tdrs/system-modules.md"
  - "docs/features/knowledge.feature"
