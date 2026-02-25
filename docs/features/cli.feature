Feature: Cliplin CLI Tool
  As a developer
  I want to install and use the Cliplin CLI tool
  So that I can initialize Cliplin projects with proper configuration for AI-assisted development

  Background:
    Given the system has Python 3.10 or higher installed
    And the system has `uv` (Astral UV) installed and available in PATH

  @status:implemented
  @changed:2024-01-15
  Scenario: Install CLI tool via uv tool install
    Given I have `uv` installed and available in PATH
    When I run `uv tool install cliplin`
    Then the installation should complete successfully
    And the `cliplin` command should be available in PATH
    And I should be able to run `cliplin --version` successfully
    And I should be able to run `cliplin --help` successfully

  @status:modified
  @changed:2025-02-23
  @reason:Framework ADRs moved to built-in package in .cliplin/knowledge/cliplin-framework
  Scenario: Initialize a new Cliplin project with default AI tool
    Given I have the Cliplin CLI tool installed
    And I am in an empty directory or a new project directory
    When I run `cliplin init`
    Then the CLI should create configuration files in the current directory
    And the CLI should create the required Cliplin directory structure:
      | Directory | Purpose |
      | docs/adrs | Project Architecture Decision Records (user-created) |
      | docs/business | Business documentation |
      | docs/features | Feature files (Gherkin) |
      | docs/tdrs | Technical Decision Records (TDR) |
      | docs/ui-intent | UI Intent specifications |
      | .cliplin/data/context | Context store (project context store) |
    And the CLI should create the built-in framework package at `.cliplin/knowledge/cliplin-framework/`
    And the CLI should create framework ADRs in `.cliplin/knowledge/cliplin-framework/docs/adrs/`:
      | File | Content |
      | 000-cliplin-framework.md | Cliplin Framework Overview |
      | 001-ts4-format.md | TS4 Format and Usage (legacy) |
      | 003-tdr-format.md | TDR Format and Usage |
      | 002-ui-intent-format.md | UI Intent Schema Format |
      | 005-knowledge-packages.md | Knowledge Packages ADR |
    And the CLI should NOT add the framework package to `cliplin.yaml` (it is a hidden built-in package)
    And the CLI should initialize the context store at `.cliplin/data/context`
    And the CLI should create the required context store collections:
      | Collection Name | Purpose |
      | business-and-architecture | Stores ADRs and business documentation |
      | features | Stores feature files |
      | technical-decision-records | Stores TDR technical specifications |
      | tech-specs | Stores legacy TS4 technical specifications |
      | uisi | Stores UI Intent YAML files |
    And the CLI should ensure `.cliplin` is listed in `.gitignore`
    And the CLI should validate that the project structure is correct
    And the CLI should index the framework package into the context store automatically
    And the CLI should display a success message indicating project initialization is complete

  @status:implemented
  @changed:2024-01-15
  Scenario: Initialize a Cliplin project with specific AI tool (Cursor)
    Given I have the Cliplin CLI tool installed
    And I am in an empty directory or a new project directory
    When I run `cliplin init --ai cursor`
    Then the CLI should create configuration files in the current directory
    And the CLI should generate configuration files adjusted for the AI tool ID "cursor"
    And the CLI should create `.cursor/rules/` directory structure
    And the CLI should create MCP server configuration files for Cursor
    And the CLI should create `.cursor/mcp.json` if it does not exist
    And the CLI should configure `.cursor/mcp.json` with Cliplin context MCP server configuration
    And the CLI should configure the Cliplin context MCP server for Cursor integration
    And the CLI should create `.cursor/rules/context.mdc` with Cliplin context MCP configuration
    And the CLI should create `.cursor/rules/feature-processing.mdc` with feature processing rules
    And the CLI should ensure `.cliplin` is listed in `.gitignore`
    And the CLI should validate that Cursor-specific configurations are correct
    And the CLI should initialize context store collections as specified in the context rules
    And the CLI should display a success message indicating project initialization with Cursor is complete

  @status:implemented
  @changed:2024-01-15
  Scenario: Initialize a Cliplin project with specific AI tool (Claude Desktop)
    Given I have the Cliplin CLI tool installed
    And I am in an empty directory or a new project directory
    When I run `cliplin init --ai claude-desktop`
    Then the CLI should create configuration files in the current directory
    And the CLI should generate configuration files adjusted for the AI tool ID "claude-desktop"
    And the CLI should create `.claude/` directory structure
    And the CLI should create `.claude/rules/` directory structure for rule files
    And the CLI should create MCP server configuration files for Claude Desktop
    And the CLI should create `.mcp.json` at the root of the project if it does not exist
    And the CLI should configure `.mcp.json` with Cliplin MCP server configuration
    And the CLI should create `.claude/claude.md` with instructions on how to use the rules
    And the CLI should configure the Cliplin MCP server for Claude Desktop integration
    And the CLI should ensure `.cliplin` is listed in `.gitignore`
    And the CLI should validate that Claude Desktop-specific configurations are correct
    And the CLI should initialize context store collections as specified in the context rules
    And the CLI should display a success message indicating project initialization with Claude Desktop is complete

  @status:implemented
  @changed:2025-02-16
  @reason:Config file default location moved to project root
  Scenario: Validate project structure after initialization
    Given I have initialized a Cliplin project using `cliplin init --ai cursor`
    When I run `cliplin validate` or the validation runs automatically after init
    Then the CLI should verify that all required directories exist:
      | docs/adrs |
      | docs/business |
      | docs/features |
      | docs/tdrs |
      | docs/ui-intent |
      | .cliplin/data/context |
    And the CLI should verify that the context store exists at `.cliplin/data/context`
    And the CLI should verify that all required context store collections exist:
      | business-and-architecture |
      | features |
      | technical-decision-records |
      | tech-specs |
      | uisi |
    And the CLI should verify that configuration file exists at project root `cliplin.yaml`
    And the CLI should verify that MCP server configuration files exist for the specified AI tool
    And if the AI tool is "cursor", the CLI should verify that `.cursor/mcp.json` exists
    And if the AI tool is "claude-desktop", the CLI should verify that `.mcp.json` exists at the project root
    And the CLI should verify that Python version is 3.10 or higher
    And the CLI should verify that required dependencies are available
    And if any validation fails, the CLI should display clear error messages indicating what is missing or incorrect

  @status:implemented
  @changed:2024-01-15
  Scenario: Initialize project with Cliplin context MCP server configuration
    Given I have the Cliplin CLI tool installed
    And I am in a directory where I want to initialize a Cliplin project
    When I run `cliplin init --ai cursor`
    Then the CLI should create MCP server configuration that enables Cliplin context access
    And the CLI should create `.cursor/mcp.json` with MCP server configuration
    And the `.cursor/mcp.json` file should define the Cliplin context MCP server with:
      | Field | Description |
      | mcpServers | Object containing server configurations |
      | cliplin-context | Server identifier for Cliplin context MCP |
      | command | Command to start the Cliplin MCP server |
      | args | Arguments for the MCP server |
    And the MCP server configuration should use the project context store path (e.g. `.cliplin/data/context`)
    And the MCP server configuration should define the collection mappings:
      | Collection | File Pattern | Directory |
      | business-and-architecture | *.md | docs/adrs, docs/business |
      | features | *.feature | docs/features |
      | technical-decision-records | *.md | docs/tdrs |
      | tech-specs | *.ts4 | docs/ts4 |
      | uisi | *.yaml | docs/ui-intent |
    And the MCP server configuration should be accessible to the AI tool (Cursor)
    And the AI tool should be able to query and update the context store collections via MCP

  @status:modified
  @changed:2024-01-15
  @reason:Added-context-loading-protocol-requirement
  Scenario: Initialize project with AI rules and conventions
    Given I have the Cliplin CLI tool installed
    And I am in an empty directory or a new project directory
    When I run `cliplin init --ai cursor`
    Then the CLI should create rule files that define:
      | Rule File | Purpose |
      | .cursor/rules/context.mdc | Context indexing rules and context store collection mappings |
      | .cursor/rules/feature-processing.mdc | Feature file processing and implementation rules |
      | .cursor/rules/context-protocol-loading.mdc | Context loading protocol rules |
    And the rule files should specify automatic indexing behavior for context files
    And the rule files should specify user confirmation requirements before indexing
    And the rule files should define metadata requirements for indexed documents
    And the rule files should specify feature lifecycle management (pending, implemented, deprecated)
    And the rule files should define impact analysis requirements for feature changes
    And the rule files should define context loading protocol requiring AI assistants to query the context store (via Cliplin MCP) before starting any task

  @status:implemented
  @changed:2024-01-15
  Scenario: Handle initialization in non-empty directory
    Given I have the Cliplin CLI tool installed
    And I am in a directory that already contains some files
    When I run `cliplin init --ai cursor`
    Then the CLI should check if Cliplin is already initialized
    And if Cliplin is already initialized, the CLI should display a warning message
    And the CLI should ask for confirmation before overwriting existing Cliplin configuration
    And if `.cursor/mcp.json` already exists, the CLI should check if it contains Cliplin MCP server configuration
    And if `.cursor/mcp.json` exists and contains Cliplin configuration, the CLI should preserve existing MCP server entries
    And if `.cursor/mcp.json` exists but does not contain Cliplin configuration, the CLI should add the Cliplin MCP server configuration
    And if the user confirms, the CLI should proceed with initialization
    And when the user has confirmed on an already-initialized project, the CLI should run knowledge install at the end to reinstall knowledge packages listed in cliplin.yaml
    And if the user declines, the CLI should abort without making changes
    And if Cliplin is not initialized, the CLI should proceed with initialization normally

  @status:new
  @changed:2025-02-23
  Scenario: Built-in framework package is hidden and updated on every init
    Given I have the Cliplin CLI tool installed
    And I am in an empty directory or a new project directory
    When I run `cliplin init`
    Then the CLI should create the built-in framework package at `.cliplin/knowledge/cliplin-framework/`
    And the framework package should contain framework ADRs in `docs/adrs/` (000, 001, 002, 003, 005)
    And the framework package should NOT appear in `cliplin.yaml` under the `knowledge` key
    And the framework package should NOT be listed by `cliplin knowledge list` (it is hidden)
    When I run `cliplin init` again and confirm to continue
    Then the CLI should update the framework package at `.cliplin/knowledge/cliplin-framework/` with the latest framework content
    And the framework ADRs should be overwritten with the current templates

  @status:implemented
  @changed:2025-02-16
  @reason:Config file default location moved to project root
  Scenario: Create configuration files during initialization
    Given I have the Cliplin CLI tool installed
    And I am in an empty directory or a new project directory
    When I run `cliplin init --ai cursor`
    Then the CLI should create `cliplin.yaml` at project root with proper configuration
    And the CLI should create `README.md` if it doesn't exist
    And the CLI should include the AI tool configuration in the config file
    And the CLI should display success messages for each created file

  @status:implemented
  @changed:2024-01-15
  Scenario: Handle invalid AI tool ID
    Given I have the Cliplin CLI tool installed
    And I am in an empty directory or a new project directory
    When I run `cliplin init --ai invalid-tool`
    Then the CLI should display an error message indicating that the AI tool ID is not recognized
    And the CLI should list available AI tool IDs (e.g., "cursor", "claude-desktop")
    And the CLI should exit with a non-zero status code
    And no files should be created in the current directory

  @status:implemented
  @changed:2024-01-15
  Scenario: Display help information
    Given I have the Cliplin CLI tool installed
    When I run `cliplin --help`
    Then the CLI should display usage information
    And the CLI should list all available commands (init, validate, reindex, feature apply, knowledge, etc.)
    And the CLI should show command options and arguments
    And the CLI should display examples of command usage
    And the CLI should show the `reindex` command with its options:
      | Option | Description |
      | --type | Reindex files of a specific type (ts4, feature, md, yaml) |
      | --directory | Reindex all files in a specific directory |
      | --dry-run | Review changes without reindexing |
      | --verbose | Display detailed output |
      | --interactive | Prompt for confirmation before reindexing |
    And the CLI should show the `feature apply` command with its description:
      | Command | Description |
      | feature apply <feature_filepath> | Generate an implementation prompt for a feature file |

  @status:implemented
  @changed:2024-01-15
  Scenario: Display version information
    Given I have the Cliplin CLI tool installed
    When I run `cliplin --version`
    Then the CLI should display the version number
    And the CLI should display the Python version being used
    And the CLI should display the uv version if available

  @status:implemented
  @changed:2024-01-15
  Scenario: Reindex all context files
    Given I have initialized a Cliplin project using `cliplin init --ai cursor`
    And the context store exists at `.cliplin/data/context`
    And there are context files in the project directories
    When I run `cliplin reindex`
    Then the CLI should scan for context files in the following directories:
      | Directory | File Pattern | Collection |
      | docs/adrs | *.md | business-and-architecture |
      | docs/business | *.md | business-and-architecture |
      | docs/features | *.feature | features |
      | docs/tdrs | *.md | technical-decision-records |
      | docs/ts4 | *.ts4 | tech-specs |
      | docs/ui-intent | *.yaml | uisi |
      | .cliplin/knowledge/** | *.md, *.feature, *.yaml | same as project docs |
    And the CLI should check if each file already exists in the context store by file path
    And for each file that exists, the CLI should update it in the context store
    And for each file that does not exist, the CLI should add it to the context store
    And the CLI should include proper metadata for each document:
      | Metadata Field | Description |
      | file_path | Relative path to file from project root |
      | type | File type (tdr, ts4, adr, project-doc, feature, ui-intent) |
      | collection | Target collection name |
    And the CLI should use the file path as the document ID
    And the CLI should display a summary of reindexing results:
      | Files Added | Files Updated | Files Skipped | Errors |
    And the CLI should display success message indicating reindexing is complete

  @status:implemented
  @changed:2024-01-15
  Scenario: Reindex specific context file
    Given I have initialized a Cliplin project using `cliplin init --ai cursor`
    And the context store exists at `.cliplin/data/context`
    And there is a file `docs/tdrs/my-spec.md` in the project
    When I run `cliplin reindex docs/tdrs/my-spec.md`
    Then the CLI should validate that the file exists
    And the CLI should determine the target collection based on file type and location:
      | File Path | Collection |
      | docs/tdrs/*.md | technical-decision-records |
      | docs/ts4/*.ts4 | tech-specs |
      | docs/adrs/*.md | business-and-architecture |
      | docs/business/*.md | business-and-architecture |
      | docs/features/*.feature | features |
      | docs/ui-intent/*.yaml | uisi |
    And the CLI should check if the file already exists in the context store
    And if the file exists, the CLI should update it with new content
    And if the file does not exist, the CLI should add it to the context store
    And the CLI should include proper metadata with file_path, type, and collection
    And the CLI should display a success message indicating the file was reindexed

  @status:implemented
  @changed:2024-01-15
  Scenario: Reindex all files of a specific type (TS4)
    Given I have initialized a Cliplin project using `cliplin init --ai cursor`
    And the context store exists at `.cliplin/data/context`
    And there are multiple `.ts4` files in `docs/ts4/` directory
    When I run `cliplin reindex --type ts4`
    Then the CLI should scan for all `.ts4` files in `docs/ts4/` directory
    And the CLI should reindex each `.ts4` file to the `tech-specs` collection
    And the CLI should process each file with proper metadata
    And the CLI should display a summary showing how many TS4 files were reindexed

  @status:implemented
  @changed:2024-01-15
  Scenario: Reindex all files of a specific type (features)
    Given I have initialized a Cliplin project using `cliplin init --ai cursor`
    And the context store exists at `.cliplin/data/context`
    And there are multiple `.feature` files in `docs/features/` directory
    When I run `cliplin reindex --type feature`
    Then the CLI should scan for all `.feature` files in `docs/features/` directory
    And the CLI should reindex each `.feature` file to the `features` collection
    And the CLI should process each file with proper metadata
    And the CLI should display a summary showing how many feature files were reindexed

  @status:implemented
  @changed:2024-01-15
  Scenario: Reindex all files in a specific directory
    Given I have initialized a Cliplin project using `cliplin init --ai cursor`
    And the context store exists at `.cliplin/data/context`
    And there are multiple files in `docs/business/` directory
    When I run `cliplin reindex --directory docs/business`
    Then the CLI should scan for all `.md` files in `docs/business/` directory
    And the CLI should reindex each file to the `business-and-architecture` collection
    And the CLI should determine the correct collection based on directory:
      | Directory | Collection |
      | docs/adrs | business-and-architecture |
      | docs/business | business-and-architecture |
      | docs/features | features |
      | docs/tdrs | technical-decision-records |
      | docs/ts4 | tech-specs |
      | docs/ui-intent | uisi |
    And the CLI should process each file with proper metadata
    And the CLI should display a summary showing how many files were reindexed

  @status:implemented
  @changed:2024-01-15
  Scenario: Review changes in context files without reindexing
    Given I have initialized a Cliplin project using `cliplin init --ai cursor`
    And the context store exists at `.cliplin/data/context`
    And there are context files in the project
    When I run `cliplin reindex --dry-run`
    Then the CLI should scan for context files in all context directories
    And the CLI should check which files exist in the context store
    And the CLI should detect which files have been modified since last indexing
    And the CLI should display a report showing:
      | File Path | Status | Action |
      | docs/tdrs/new-file.md | New | Would add |
      | docs/tdrs/existing-file.md | Modified | Would update |
      | docs/tdrs/unchanged-file.md | Unchanged | Would skip |
    And the CLI should not make any changes to the context store
    And the CLI should display a summary of what would be reindexed

  @status:implemented
  @changed:2024-01-15
  Scenario: Handle reindexing when context store is not initialized
    Given I have initialized a Cliplin project using `cliplin init --ai cursor`
    And the context store does not exist at `.cliplin/data/context`
    When I run `cliplin reindex`
    Then the CLI should detect that the context store is not initialized
    And the CLI should display an error message indicating that the project must be initialized first (e.g. run `cliplin init`)
    And the CLI should suggest running `cliplin init` to initialize the project
    And the CLI should exit with a non-zero status code

  @status:implemented
  @changed:2024-01-15
  Scenario: Handle reindexing when file does not exist
    Given I have initialized a Cliplin project using `cliplin init --ai cursor`
    And the context store exists at `.cliplin/data/context`
    When I run `cliplin reindex docs/tdrs/non-existent-file.md`
    Then the CLI should validate that the file exists
    And the CLI should display an error message indicating that the file does not exist
    And the CLI should exit with a non-zero status code
    And no changes should be made to the context store

  @status:implemented
  @changed:2024-01-15
  Scenario: Handle reindexing file outside context directories
    Given I have initialized a Cliplin project using `cliplin init --ai cursor`
    And the context store exists at `.cliplin/data/context`
    And there is a file `src/main.py` in the project
    When I run `cliplin reindex src/main.py`
    Then the CLI should validate that the file is in a context directory
    And the CLI should display an error message indicating that the file is not in a valid context directory
    And the CLI should list valid context directories:
      | docs/adrs |
      | docs/business |
      | docs/features |
      | docs/tdrs |
      | docs/ui-intent |
    And the CLI should exit with a non-zero status code

  @status:implemented
  @changed:2024-01-15
  Scenario: Reindex with verbose output
    Given I have initialized a Cliplin project using `cliplin init --ai cursor`
    And the context store exists at `.cliplin/data/context`
    And there are context files in the project
    When I run `cliplin reindex --verbose`
    Then the CLI should display detailed information for each file being processed:
      | File Path | Collection | Action | Status |
    And the CLI should display metadata being added for each file
    And the CLI should display any warnings or errors encountered during processing
    And the CLI should provide progress indicators for large batches of files

  @status:implemented
  @changed:2024-01-15
  Scenario: Reindex with confirmation prompt
    Given I have initialized a Cliplin project using `cliplin init --ai cursor`
    And the context store exists at `.cliplin/data/context`
    And there are context files in the project
    When I run `cliplin reindex --interactive`
    Then the CLI should scan for context files
    And the CLI should display a list of files that will be reindexed
    And the CLI should prompt for confirmation: "Reindex X files? (y/n)"
    And if the user confirms (y/yes), the CLI should proceed with reindexing
    And if the user declines (n/no), the CLI should abort without making changes
    And the CLI should display a message indicating the action taken

  @status:implemented
  @changed:2024-01-15
  Scenario: Reindex and handle duplicate documents
    Given I have initialized a Cliplin project using `cliplin init --ai cursor`
    And the context store exists at `.cliplin/data/context`
    And a file `docs/tdrs/test.md` already exists in the context store with the same file path ID
    When I run `cliplin reindex docs/tdrs/test.md`
    Then the CLI should detect that the document already exists in the context store
    And the CLI should update the existing document instead of creating a duplicate
    And the CLI should use the MCP update-documents tool instead of add-documents
    And the CLI should update the document content, metadata, and embeddings
    And the CLI should display a message indicating the file was updated

  @status:implemented
  @changed:2024-01-15
  Scenario: Reindex with collection validation
    Given I have initialized a Cliplin project using `cliplin init --ai cursor`
    And the context store exists at `.cliplin/data/context`
    And all required collections exist in the context store
    When I run `cliplin reindex`
    Then the CLI should verify that all required collections exist:
      | business-and-architecture |
      | features |
      | technical-decision-records |
      | tech-specs |
      | uisi |
    And if any collection is missing, the CLI should create it before reindexing
    And the CLI should use the correct collection for each file type
    And the CLI should display an error if it cannot access or create a collection

  @status:implemented
  @changed:2024-01-15
  Scenario: Generate implementation prompt for a feature file
    Given I have initialized a Cliplin project using `cliplin init --ai cursor`
    And the context store exists at `.cliplin/data/context`
    And there is a feature file `docs/features/my-feature.feature` in the project
    When I run `cliplin feature apply docs/features/my-feature.feature`
    Then the CLI should validate that the feature file exists
    And the CLI should generate a structured implementation prompt
    And the CLI should output the prompt to stdout
    And the CLI should exit with a zero status code

  @status:implemented
  @changed:2024-01-15
  Scenario: Handle feature apply when feature file does not exist
    Given I have initialized a Cliplin project using `cliplin init --ai cursor`
    And the context store exists at `.cliplin/data/context`
    When I run `cliplin feature apply docs/features/non-existent.feature`
    Then the CLI should validate that the feature file exists
    And the CLI should display an error message indicating that the feature file does not exist
    And the CLI should exit with a non-zero status code
    And no prompt should be generated

  @status:implemented
  @changed:2024-01-15
  Scenario: Handle feature apply when context store is not initialized
    Given I have initialized a Cliplin project using `cliplin init --ai cursor`
    And the context store does not exist at `.cliplin/data/context`
    And there is a feature file `docs/features/my-feature.feature` in the project
    When I run `cliplin feature apply docs/features/my-feature.feature`
    Then the CLI should detect that the context store is not initialized
    And the CLI should display an error message indicating that the project must be initialized first (e.g. run `cliplin init`)
    And the CLI should suggest running `cliplin init` to initialize the project
    And the CLI should exit with a non-zero status code
    And no prompt should be generated

  @status:implemented
  @changed:2024-01-15
  Scenario: Handle feature apply when feature file is outside features directory
    Given I have initialized a Cliplin project using `cliplin init --ai cursor`
    And the context store exists at `.cliplin/data/context`
    And there is a file `src/main.py` in the project
    When I run `cliplin feature apply src/main.py`
    Then the CLI should validate that the file is in the `docs/features/` directory
    And the CLI should display an error message indicating that the file is not a valid feature file
    And the CLI should suggest using a file from `docs/features/` directory
    And the CLI should exit with a non-zero status code
    And no prompt should be generated

