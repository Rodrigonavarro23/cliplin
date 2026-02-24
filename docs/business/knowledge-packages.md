# Knowledge Packages

Cliplin can manage **knowledge packages**: external repositories that contain ADRs, TS4, business docs, features, rules, or skills. Those packages are installed under your project and **indexed in the same context store** as your own specs, so the AI can use them as context.

---

## 1. Configuration

In `cliplin.yaml` at project root, add a `knowledge` section with a list of packages:

```yaml
knowledge:
  - name: aws
    source: github:Rodrigonavarro23/cliplin-knowledge
    version: main
  - name: commons
    source: github:myorg/cross-knowledge
    version: v1.0.0
```

- **name**: Logical name of the package (e.g. `aws`, `commons`). May include a subpath (e.g. `AWS/aws-sqs`) to install only a nested subfolder from a monorepo.
- **source**: Repository location. Supported formats:
  - `github:owner/repo`
  - `https://github.com/owner/repo.git`
  - `owner/repo` (treated as GitHub).
- **version**: Branch name, tag, or commit SHA (e.g. `main`, `v1.0.0`, `abc123`).

You can edit this by hand or use the CLI (see below); the CLI keeps the file valid and preserves other keys (e.g. `ai_tool`).

---

## 2. Two Ways Repos Can Be Structured

### Multi-package repo (one repo, many packages)

The repository has **one top-level folder per package** (e.g. `aws/`, `commons/`, `redis/`). The **name** in `cliplin.yaml` selects which folder to install.

Example: repo structure:

```
repo/
├── aws/
│   ├── adrs/
│   ├── ts4/
│   └── ...
├── commons/
│   ├── docs/adrs/
│   └── ...
└── redis/
```

When you run `cliplin knowledge add aws github:org/repo main`, only the **content of the `aws/` folder** is installed under `.cliplin/knowledge/aws-.../` (with `adrs/`, `ts4/`, etc. at the root of that directory). The same repo can provide several packages with different names.

### Nested subpath (monorepo with parent folder)

If the repo has a parent folder with subfolders (e.g. `AWS/aws-sqs`, `AWS/aws-dynamo`, `AWS/aws-s3`), you can install a single subfolder by using the path as the name:

```bash
cliplin knowledge add AWS/aws-sqs github:org/repo main
```

- **name**: `AWS/aws-sqs` (the path in the repo)
- **source**: `github:org/repo` (the repo URL, no subpath)
- **Result**: `.cliplin/knowledge/AWS-aws-sqs-.../` contains only the content of `AWS/aws-sqs` (flattened to the package root)

Use quotes in the shell if needed: `cliplin knowledge add "AWS/aws-sqs" github:org/repo main`.

### Single-package repo (whole repo is one package)

The repository **root** contains the usual Cliplin layout (`docs/adrs/`, `docs/tdrs/`, etc.). There is no top-level folder matching the package name. In that case, Cliplin installs the root-level context paths and the package root is the repo root.

---

## 3. Commands

All commands must be run from the project root (where `cliplin.yaml` is). The project must be initialized with `cliplin init` first.

### List packages

```bash
cliplin knowledge list
```

Shows each package in `cliplin.yaml` with name, source, version, and whether it is installed (directory exists under `.cliplin/knowledge/`).

### Add a package

```bash
cliplin knowledge add <name> <source> <version>
```

Example:

```bash
cliplin knowledge add aws github:Rodrigonavarro23/cliplin-knowledge main
```

- Adds the entry to `cliplin.yaml`.
- Clones the repo with **sparse checkout** (only the needed paths or the `<name>/` subfolder).
- Installs under `.cliplin/knowledge/<name>-<source_normalized>/`.
- **Reindexes** that package so its content is in the context store (business-and-architecture, tech-specs, features, uisi as per file type).
- If your host supports skills (e.g. Claude Desktop or Cursor), skills from the package are linked under the host's skills directory (`.claude/skills/` or `.cursor/skills/`).

### Remove a package

```bash
cliplin knowledge remove <name>
```

- Removes the entry from `cliplin.yaml`.
- Deletes the package directory under `.cliplin/knowledge/`.
- **Removes all documents** that belonged to that package from the context store and updates the fingerprint store.
- Removes skill links (e.g. under `.claude/skills/` or `.cursor/skills/`) if the host integration created them.

### Update a package

```bash
cliplin knowledge update <name>
# or to a specific version:
cliplin knowledge update <name> --version v2.0.0
```

- Fetches and checks out the given (or configured) version.
- Refreshes the package content and re-flattens it if the repo is multi-package.
- Reindexes the package so the context store is up to date.

Use this after the upstream repo changes (e.g. you renamed `adr` to `adrs` or added new specs).

### Show package details

```bash
cliplin knowledge show <name>
```

Shows name, source, version, install path, whether it is installed, and the **number of files** in the package directory (excluding `.git`).

### Install all packages

```bash
cliplin knowledge install
# or reinstall all (remove + clone fresh with configured version):
cliplin knowledge install --force
```

- **Without `--force`**: For each package in `cliplin.yaml`, adds it if not installed or updates it if already installed. Idempotent sync.
- **With `--force`**: For each package, removes its directory (and purges context store and fingerprint store), then clones fresh using the version in `cliplin.yaml`. Does not change the version in config. Use after corruption or to get a clean copy.

Useful after cloning a project that has `knowledge: [...]` in `cliplin.yaml` but no `.cliplin/knowledge/` (e.g. it is gitignored).

---

## 4. Where things are installed

- **Root**: `.cliplin/knowledge/`
- **Per package**: `.cliplin/knowledge/<name>-<source_normalized>/`  
  Example: `aws-github-Rodrigonavarro23-cliplin-knowledge`.

The content inside each package directory follows the same layout as your project (e.g. `adrs/`, `ts4/`, `docs/features/`), so the same indexing rules apply.

---

## 5. Reindex and context store

- **After add or update**, the package is reindexed automatically; you do not need to run `cliplin reindex` for that package only.
- **After remove**, the package’s documents are removed from the context store.
- **Full reindex**: `cliplin reindex` also scans `.cliplin/knowledge/**` and indexes all packages. You can limit to knowledge with:
  ```bash
  cliplin reindex --directory .cliplin/knowledge
  ```

Documents from knowledge packages use the same collections as your own specs (e.g. ADRs → `business-and-architecture`, TS4 → `tech-specs`). The AI sees them when loading context via the Cliplin MCP.

---

## 6. Conventions in package repos

For content to be indexed correctly, package repos should use the usual Cliplin paths:

- **ADRs / business**: `adrs/`, `docs/adrs/`, `business/`, `docs/business/` (with `.md`).
- **TDR**: `tdrs/`, `docs/tdrs/` (with `.md`). Legacy: **TS4** `ts4/`, `docs/ts4/` (with `.ts4`).
- **Features**: `features/`, `docs/features/` (with `.feature`).
- **UI intent**: `ui-intent/`, `docs/ui-intent/` (with `.yaml`).
- **Skills** (optional): folders containing `SKILL.md` under `skills/` (e.g. `skills/skill-folder/SKILL.md` or `skills/<pkg>/skill-folder/SKILL.md`) — if the host supports skills (e.g. Claude Desktop, Cursor), Cliplin finds all folders that contain `SKILL.md` and creates hard links under the host's skills directory (`.claude/skills/` or `.cursor/skills/`), one level only (e.g. `.claude/skills/skill-folder/SKILL.md` or `.cursor/skills/skill-folder/SKILL.md`).

Nested subfolders (e.g. `adrs/framework/001-foo.md`) are supported; indexing is structure-agnostic within these path patterns.

---

## References

- **ADR**: [005-knowledge-packages.md](../adrs/005-knowledge-packages.md)
- **Feature**: [knowledge.feature](../features/knowledge.feature)
- **TS4**: [knowledge-packages.ts4](../ts4/knowledge-packages.ts4), [knowledge-reindex-context.ts4](../ts4/knowledge-reindex-context.ts4)
