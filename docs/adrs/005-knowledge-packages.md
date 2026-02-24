# ADR-005: Knowledge Packages (Cliplin as Knowledge Package Manager)

## Status
Accepted

## Context

Teams and projects need to reuse specification knowledge (ADRs, TS4, business docs, features, rules, skills) across repositories without duplicating content. Copy-pasting or manual symlinks do not scale and break versioning. We need a way to:

1. **Declare dependencies** on external knowledge packages (e.g. shared ADRs, company TS4, domain features).
2. **Install and version** those packages in a predictable location under the project.
3. **Integrate with the context store**: content from packages must be indexed and queryable like project-owned docs (same collections, same RAG behavior).
4. **Keep the store consistent**: adding, updating, or removing a package must trigger reindexing so the context reflects current dependencies; removing a package must remove its documents from the store.
5. **Expose host-specific assets** (e.g. skills) when the AI host supports them, without breaking hosts that do not.

Cliplin already has a context store (ADR-002), incremental reindexing (ADR-003), and a single source of truth for context locations (TS4 system-modules). Extending that model to a dedicated "knowledge" directory and a CLI command to manage packages aligns with the existing architecture.

## Decision

**Introduce knowledge packages as a first-class concept and add the `cliplin knowledge` command as the package manager for Cliplin knowledge (ADRs, TS4, business, rules, skills, etc.).**

### 1. Declaration and configuration

- **Source of truth for the package list**: The project config file `cliplin.yaml` at project root SHALL have an optional top-level key `knowledge`, whose value is a list of package entries.
- **Package entry schema**: Each entry SHALL have:
  - `name`: string, logical name of the package (e.g. `commons`, `redis`, `databases`). MAY contain a subpath (e.g. `AWS/aws-sqs`) to install a nested subfolder from a monorepo; the path is used for sparse checkout and flattened to the package root.
  - `source`: string, location of the package (e.g. `github:org/repo`). Format and supported backends (e.g. GitHub) are defined in TS4; the ADR does not fix the exact URI scheme.
  - `version`: string, version specifier (branch name, commit SHA, or version tag). Used when cloning or updating the package.
- **Example** (YAML structure only; exact keys are normative in TS4):

  ```yaml
  knowledge:
    - name: commons
      source: github:something/cross-knowledge/commons
      version: main
    - name: redis
      source: github:something/cross-knowledge/redis
      version: v1.0.0
  ```

### 2. Installation location and layout

- **Installation root**: All knowledge packages SHALL be installed under `.cliplin/knowledge/` (under the project root).
- **Per-package directory name**: Each package SHALL live in a directory named `<name>-<source_normalized>`, where `source_normalized` is the source string in a form safe for the filesystem (e.g. colons or slashes replaced by a consistent character so the path is unique and valid on all supported OS). Example: `.cliplin/knowledge/commons-github:something/cross-knowledge/commons`.
- **Content**: Package content is obtained by cloning the repository (or equivalent) and, where supported, using **git sparse checkout** so only the relevant paths are materialized. Technical details (sparse-checkout paths, clone vs shallow) are specified in TS4.
- **Name with subpath (nested subfolders)**: The package **name** MAY be a path with slashes (e.g. `AWS/aws-sqs`) to install a nested subfolder from a monorepo. Sparse checkout SHALL use that path; the content SHALL be flattened to the package root.
- **Name as top-level (multi-package repos)**: A repository MAY contain multiple packages as top-level subfolders (e.g. `aws/`, `commons/`, `redis/`). In that case, the package **name** SHALL identify which subfolder to install: only that subfolder’s content is materialized (sparse checkout restricted to `<name>/`). The installed directory SHALL contain that subfolder’s content at its root (so the package root equals the content of `repo/<name>/`). If the repository has no top-level folder matching the name (single-package repo with e.g. `docs/`, `ts4/` at root), the implementation SHALL materialize the root-level context paths (e.g. `docs/adrs`, `docs/ts4`, …) so that layout is also supported.

### 3. Context store and reindexing

- **Same collections as project docs**: Documents inside `.cliplin/knowledge/**` SHALL be treated as project context. The same collection mapping applies: e.g. ADRs (under any `adrs` or `docs/adrs`-like path within a package) → `business-and-architecture`; TS4 → `tech-specs`; features → `features`; business docs → `business-and-architecture`; UI intent → `uisi`. The mapping and directory scanning SHALL be defined in one place (single source of truth) and SHALL include knowledge package roots; see TS4 knowledge-reindex-context.
- **Structure-agnostic indexing**: Indexing SHALL traverse each package directory recursively. Any `.md` under an adr-like path, any `.ts4`, any `.feature`, any `.yaml` under ui-intent-like paths, etc., SHALL be included regardless of internal subfolder structure (flat or nested). All relevant files under a given topic (e.g. adrs) SHALL be indexed into the corresponding collection.
- **Document IDs and metadata**: Document IDs (e.g. file path relative to project root) SHALL include the path within the project so that `.cliplin/knowledge/commons-.../docs/adrs/001-foo.md` is uniquely identified and can be updated or deleted when the package is updated or removed.
- **Reindex after add/update/remove**: After `knowledge add` or `knowledge update`, the implementation SHALL trigger reindexing (or equivalent index updates) for the affected package so the context store reflects the new or changed content. After `knowledge remove`, the implementation SHALL remove from the context store all documents that belonged to that package and SHALL update the fingerprint store accordingly so the system stays consistent with ADR-002 and ADR-003.

### 4. Skills and host-specific behavior

- **Host-specific**: How (or whether) to expose package content that is host-specific (e.g. **skills**) is left to each AI host integration. There is no requirement that all hosts support the same behavior.
- **Supporting hosts**: If an integration supports skills (e.g. Claude Desktop, Cursor), it MAY expose skills from installed knowledge packages via hard links under the host's skills directory (e.g. `.claude/skills`, `.cursor/skills`) so they appear as installed to the host. On `knowledge remove`, those links SHALL be removed so the host no longer sees the package’s skills.
- **Non-supporting hosts**: If an integration does not support skills (or does not implement this behavior), it SHALL perform no action for skills; the rest of the knowledge feature (context store, reindex) still applies.

### 5. CLI command

- **Command name**: `cliplin knowledge` with subcommands: `list`, `add`, `remove`, `update`, `show` (or equivalent). Exact subcommand names and options are specified in the feature file and TS4.
- **Responsibilities**: The command SHALL read and write `cliplin.yaml` for the package list, SHALL install/update/remove packages under `.cliplin/knowledge/`, and SHALL trigger reindex (and skill link updates where applicable) so that the project’s context and host-specific assets stay consistent with the declared `knowledge` list.

## Consequences

### Positive

- **Reuse**: Shared ADRs, TS4, business rules, and skills can be consumed as versioned packages without copying.
- **Single contract**: Same context store and collection model for project and package content; one reindex flow.
- **Traceability**: Document IDs and metadata keep package-origin visible; fingerprint store and incremental reindex remain valid for package paths.
- **Host flexibility**: Skills (or other host-specific assets) can be integrated only where the host supports them.

### Negative

- **Convention and structure**: Packages are expected to follow a conventional layout (e.g. `docs/adrs`, `docs/ts4`) so that the single mapping can find them; non-standard layouts may require configuration or may not be fully indexed.
- **Sparse checkout and git**: Reliance on git (and sparse checkout) ties the implementation to Git-based sources; other backends would require additional work.

### Risks and mitigations

- **Path length and reserved characters**: Normalizing `source` to a directory name must avoid invalid or overly long paths on all supported platforms; TS4 should define the normalization and any length limits.
- **Concurrent or partial updates**: Add/update/remove and reindex should be designed so that a failed reindex does not leave the store inconsistent; consider transactional or best-effort plus clear reporting.

## References

- ADR-002: ChromaDB as RAG and Context Store Base (collections, fingerprint store)
- ADR-003: Incremental Context Reindexing (reindex and fingerprint contract)
- TS4: system-modules — context locations, single source of truth for mappings
- TS4: knowledge-packages — cliplin.yaml schema, git sparse checkout, folder naming
- TS4: knowledge-reindex-context — inclusion of `.cliplin/knowledge/**` in context locations and reindex behavior
- Feature: knowledge.feature — scenarios for list, add, remove, update, show and reindex/skills integration
