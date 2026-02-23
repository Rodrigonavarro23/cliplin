Feature: Cliplin Knowledge Package Manager
  As a developer
  I want to manage knowledge packages (ADRs, TS4, business, rules, skills) via the Cliplin CLI
  So that I can reuse specification knowledge across projects as versioned dependencies and have them indexed in the project context store

  Background:
    Given I have the Cliplin CLI tool installed
    And I have initialized a Cliplin project (e.g. with `cliplin init --ai cursor`)
    And the project has a configuration file `cliplin.yaml` at project root
    And the context store is initialized at `.cliplin/data/context`

  # --- Knowledge config (cliplin.yaml) ---
  # cliplin.yaml may contain an optional top-level key "knowledge" with a list of entries.
  # Each entry: name (string), source (string, e.g. github:owner/repo), version (branch, commit, or tag).
  # Packages are installed under .cliplin/knowledge/<name>-<source_normalized>.

  @status:implemented
  @changed:2025-02-16
  Scenario: List knowledge packages declared and installed
    Given my project has a `cliplin.yaml` with a `knowledge` section containing at least one package
    When I run `cliplin knowledge list`
    Then the CLI should list each package declared in `cliplin.yaml`
    And the output should show for each package: name, source, version
    And the CLI should indicate whether each package is installed (directory exists under `.cliplin/knowledge/`)
    And if the `knowledge` section is empty or missing, the CLI should list zero packages or display an appropriate message

  @status:implemented
  @changed:2025-02-16
  Scenario: Add a knowledge package
    Given my project has `cliplin.yaml` at project root (with or without an existing `knowledge` section)
    And the package source is a valid Git repository (e.g. github:org/repo) and the version (branch, tag, or commit) exists
    When I run `cliplin knowledge add <name> <source> <version>`
    Then the CLI should add an entry to the `knowledge` section in `cliplin.yaml` with the given name, source, and version
    And the CLI should create the package directory under `.cliplin/knowledge/` with the naming convention `<name>-<source_normalized>`
    And the CLI should clone the repository using git sparse checkout so only relevant paths (e.g. docs/adrs, docs/ts4, docs/business, docs/features, rules, skills) are materialized
    And the CLI should trigger reindexing for the newly added package so its documents are indexed into the context store (business-and-architecture, tech-specs, features, uisi as per file type)
    And the CLI should display a success message
    And if the host integration supports skills (e.g. Claude Desktop), the CLI should expose package skills (e.g. via hard links under `.claude/skills`) so they appear installed to the host

  @status:implemented
  @changed:2025-02-23
  Scenario: Add a knowledge package with subpath in name (nested subfolder)
    Given my project has `cliplin.yaml` at project root
    And the package source is a valid Git repository (e.g. github:org/repo) with a nested structure (e.g. AWS/aws-sqs, AWS/aws-dynamo, AWS/aws-s3)
    And the version (branch, tag, or commit) exists
    When I run `cliplin knowledge add AWS/aws-sqs github:org/repo main`
    Then the CLI should add an entry to the `knowledge` section with name "AWS/aws-sqs", source "github:org/repo", version "main"
    And the CLI should create the package directory under `.cliplin/knowledge/` with the naming convention `AWS-aws-sqs-<source_normalized>` (slash in name normalized to hyphen)
    And the CLI should clone using sparse checkout of the path "AWS/aws-sqs" only
    And the installed package root should contain the content of AWS/aws-sqs (flattened, not nested under AWS/aws-sqs)
    And the CLI should trigger reindexing for the newly added package
    And the CLI should display a success message

  @status:implemented
  @changed:2025-02-16
  Scenario: Remove a knowledge package
    Given my project has a knowledge package installed under `.cliplin/knowledge/<package_dir>`
    And the package is listed in the `knowledge` section of `cliplin.yaml`
    When I run `cliplin knowledge remove <name>`
    Then the CLI should remove the package entry from the `knowledge` section in `cliplin.yaml`
    And the CLI should delete the package directory under `.cliplin/knowledge/`
    And the CLI should remove from the context store all documents whose path is under the removed package root
    And the CLI should update the fingerprint store to remove or invalidate entries for those document paths
    And if the host integration had created skill links for this package (e.g. under `.claude/skills`), the CLI should remove those links
    And the CLI should display a success message

  @status:implemented
  @changed:2025-02-16
  Scenario: Update a knowledge package
    Given my project has a knowledge package installed under `.cliplin/knowledge/<package_dir>`
    And the package is listed in the `knowledge` section of `cliplin.yaml` with a given version
    When I run `cliplin knowledge update <name>` (optionally with a new version)
    Then the CLI should update the clone to the specified version (or latest for the configured ref)
    And if the version in `cliplin.yaml` changes, the CLI should update the config file
    And the CLI should trigger reindexing for that package so the context store reflects the updated content
    And the CLI should display a success message

  @status:implemented
  @changed:2025-02-16
  Scenario: Show information about a knowledge package
    Given my project has at least one knowledge package declared in `cliplin.yaml` or installed under `.cliplin/knowledge/`
    When I run `cliplin knowledge show <name>`
    Then the CLI should display the package name, source, and version
    And the CLI should display the install path (e.g. `.cliplin/knowledge/<name>-<source_normalized>`)
    And the CLI may display a summary of indexed content (e.g. file counts per collection or type)
    And if the package is not declared or not installed, the CLI should display a clear error and exit with non-zero status

  @status:implemented
  @changed:2025-02-16
  Scenario: Reindex includes knowledge package content
    Given my project has one or more knowledge packages installed under `.cliplin/knowledge/`
    And at least one package contains files under paths that map to context types (e.g. docs/adrs/*.md, docs/ts4/*.ts4)
    When I run `cliplin reindex`
    Then the CLI should scan `.cliplin/knowledge/**` in addition to docs/adrs, docs/business, docs/features, docs/ts4, docs/ui-intent
    And the CLI should index each relevant file under each package into the same collections as project docs (e.g. adrs → business-and-architecture, ts4 → tech-specs)
    And the CLI should apply the same type-to-collection mapping regardless of extra subfolders inside a package (e.g. docs/adrs/framework/001-foo.md and docs/adrs/002-bar.md both map to business-and-architecture)
    And document IDs should be the file path relative to project root (e.g. `.cliplin/knowledge/commons-.../docs/adrs/001-foo.md`)

  @status:implemented
  @changed:2025-02-16
  Scenario: Handle knowledge command when cliplin.yaml is missing
    Given I am in a project directory that does not have `cliplin.yaml` at project root
    When I run `cliplin knowledge add mypkg github:org/repo main`
    Then the CLI should display a clear error indicating that the project is not initialized or config is missing
    And the CLI should exit with a non-zero status code
    And no package should be installed and no changes should be made to the filesystem

  @status:implemented
  @changed:2025-02-16
  Scenario: Display knowledge command help
    Given I have the Cliplin CLI tool installed
    When I run `cliplin knowledge --help`
    Then the CLI should display usage for the `knowledge` command
    And the CLI should list subcommands: list, add, remove, update, show, install
    And the CLI should show the `knowledge` command in the main `cliplin --help` output

  @status:implemented
  @changed:2025-02-17
  Scenario: Install all knowledge packages from cliplin.yaml
    Given my project has a `cliplin.yaml` with a `knowledge` section containing one or more packages
    And some packages may be installed and some may not
    When I run `cliplin knowledge install`
    Then the CLI should for each package declared in `cliplin.yaml`: add it if not installed, or update it if already installed
    And the CLI should create or refresh package directories under `.cliplin/knowledge/` with the naming convention `<name>-<source_normalized>`
    And the CLI should trigger reindexing for each package so its documents are indexed into the context store
    And the CLI should display a success message indicating how many packages were installed or updated
    And if the `knowledge` section is empty, the CLI should display an appropriate message and exit successfully

  @status:implemented
  @changed:2025-02-17
  Scenario: Install with --force reinstalls all packages at their configured version
    Given my project has a `cliplin.yaml` with a `knowledge` section containing one or more packages
    When I run `cliplin knowledge install --force`
    Then the CLI should for each package declared in `cliplin.yaml`: remove its directory if it exists, then clone it fresh using the version in `cliplin.yaml`
    And the CLI should NOT change the version in `cliplin.yaml` (reinstall uses the same version as configured)
    And the CLI should trigger reindexing for each package so the context store reflects the reinstalled content
    And the CLI should remove from the context store and fingerprint store any previous documents for packages that existed before reinstalling
    And the CLI should display a success message indicating how many packages were reinstalled
    And packages that were not previously installed should be installed for the first time (same behavior as add)
