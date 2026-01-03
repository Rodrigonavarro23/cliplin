@status:implemented
Feature: Cliplin CLI Tool
  As a developer
  I want to install and use the Cliplin CLI tool
  So that I can initialize Cliplin projects with proper configuration for AI-assisted development

  Background:
    Given the system has Python 3.10 or higher installed
    And the system has `uv` (Astral UV) installed and available in PATH

  Scenario: Install CLI tool via uv tool install
    Given I have `uv` installed and available in PATH
    When I run `uv tool install cliplin`
    Then the installation should complete successfully
    And the `cliplin` command should be available in PATH
    And I should be able to run `cliplin --version` successfully
    And I should be able to run `cliplin --help` successfully

  Scenario: Initialize a new Cliplin project with default AI tool
    Given I have the Cliplin CLI tool installed
    And I am in an empty directory or a new project directory
    When I run `cliplin init`
    Then the CLI should create configuration files in the current directory
    And the CLI should create the required Cliplin directory structure:
      | Directory | Purpose |
      | docs/adrs | Architecture Decision Records |
      | docs/business | Business documentation |
      | docs/features | Feature files (Gherkin) |
      | docs/ts4 | Technical specifications |
      | docs/ui-intent | UI Intent specifications |
      | .cliplin/data/context | ChromaDB context storage |
    And the CLI should initialize a ChromaDB database at `.cliplin/data/context/chroma.sqlite3`
    And the CLI should create the required ChromaDB collections:
      | Collection Name | Purpose |
      | business-and-architecture | Stores ADRs and business documentation |
      | features | Stores feature files |
      | tech-specs | Stores TS4 technical specifications |
      | uisi | Stores UI Intent YAML files |
    And the CLI should validate that the project structure is correct
    And the CLI should display a success message indicating project initialization is complete

  Scenario: Initialize a Cliplin project with specific AI tool (Cursor)
    Given I have the Cliplin CLI tool installed
    And I am in an empty directory or a new project directory
    When I run `cliplin init --ai cursor`
    Then the CLI should create configuration files in the current directory
    And the CLI should generate configuration files adjusted for the AI tool ID "cursor"
    And the CLI should create `.cursor/rules/` directory structure
    And the CLI should create MCP server configuration files for Cursor
    And the CLI should create `.cursor/mcp.json` if it does not exist
    And the CLI should configure `.cursor/mcp.json` with ChromaDB MCP server configuration
    And the CLI should configure the ChromaDB MCP server for Cursor integration
    And the CLI should create `.cursor/rules/context.mdc` with ChromaDB MCP configuration
    And the CLI should create `.cursor/rules/feature-processing.mdc` with feature processing rules
    And the CLI should validate that Cursor-specific configurations are correct
    And the CLI should initialize ChromaDB collections as specified in the context rules
    And the CLI should display a success message indicating project initialization with Cursor is complete

  Scenario: Initialize a Cliplin project with specific AI tool (Claude Desktop)
    Given I have the Cliplin CLI tool installed
    And I am in an empty directory or a new project directory
    When I run `cliplin init --ai claude-desktop`
    Then the CLI should create configuration files in the current directory
    And the CLI should generate configuration files adjusted for the AI tool ID "claude-desktop"
    And the CLI should create `.claude/` directory structure
    And the CLI should create MCP server configuration files for Claude Desktop
    And the CLI should create `.claude/mcp_config.json` if it does not exist
    And the CLI should configure `.claude/mcp_config.json` with ChromaDB MCP server configuration
    And the CLI should configure the ChromaDB MCP server for Claude Desktop integration
    And the CLI should validate that Claude Desktop-specific configurations are correct
    And the CLI should initialize ChromaDB collections as specified in the context rules
    And the CLI should display a success message indicating project initialization with Claude Desktop is complete

  Scenario: Validate project structure after initialization
    Given I have initialized a Cliplin project using `cliplin init --ai cursor`
    When I run `cliplin validate` or the validation runs automatically after init
    Then the CLI should verify that all required directories exist:
      | docs/adrs |
      | docs/business |
      | docs/features |
      | docs/ts4 |
      | docs/ui-intent |
      | .cliplin/data/context |
    And the CLI should verify that ChromaDB database file exists at `.cliplin/data/context/chroma.sqlite3`
    And the CLI should verify that all required ChromaDB collections exist:
      | business-and-architecture |
      | features |
      | tech-specs |
      | uisi |
    And the CLI should verify that configuration file exists at `.cliplin/config.yaml`
    And the CLI should verify that MCP server configuration files exist for the specified AI tool
    And if the AI tool is "cursor", the CLI should verify that `.cursor/mcp.json` exists
    And if the AI tool is "claude-desktop", the CLI should verify that `.claude/mcp_config.json` exists
    And the CLI should verify that Python version is 3.10 or higher
    And the CLI should verify that required dependencies are available
    And if any validation fails, the CLI should display clear error messages indicating what is missing or incorrect

  Scenario: Initialize project with ChromaDB MCP server configuration
    Given I have the Cliplin CLI tool installed
    And I am in a directory where I want to initialize a Cliplin project
    When I run `cliplin init --ai cursor`
    Then the CLI should create MCP server configuration that enables ChromaDB context access
    And the CLI should create `.cursor/mcp.json` with MCP server configuration
    And the `.cursor/mcp.json` file should define the ChromaDB MCP server with:
      | Field | Description |
      | mcpServers | Object containing server configurations |
      | cliplin-context | Server identifier for ChromaDB MCP |
      | command | Command to start the ChromaDB MCP server |
      | args | Arguments including database path |
    And the MCP server configuration should specify the ChromaDB database path as `.cliplin/data/context/chroma.sqlite3`
    And the MCP server configuration should define the collection mappings:
      | Collection | File Pattern | Directory |
      | business-and-architecture | *.md | docs/adrs, docs/business |
      | features | *.feature | docs/features |
      | tech-specs | *.ts4 | docs/ts4 |
      | uisi | *.yaml | docs/ui-intent |
    And the MCP server configuration should be accessible to the AI tool (Cursor)
    And the AI tool should be able to query and update the ChromaDB collections via MCP

  Scenario: Initialize project with AI rules and conventions
    Given I have the Cliplin CLI tool installed
    And I am in an empty directory or a new project directory
    When I run `cliplin init --ai cursor`
    Then the CLI should create rule files that define:
      | Rule File | Purpose |
      | .cursor/rules/context.mdc | Context indexing rules and ChromaDB collection mappings |
      | .cursor/rules/feature-processing.mdc | Feature file processing and implementation rules |
    And the rule files should specify automatic indexing behavior for context files
    And the rule files should specify user confirmation requirements before indexing
    And the rule files should define metadata requirements for indexed documents
    And the rule files should specify feature lifecycle management (pending, implemented, deprecated)
    And the rule files should define impact analysis requirements for feature changes

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
    And if the user declines, the CLI should abort without making changes
    And if Cliplin is not initialized, the CLI should proceed with initialization normally

  Scenario: Create configuration files during initialization
    Given I have the Cliplin CLI tool installed
    And I am in an empty directory or a new project directory
    When I run `cliplin init --ai cursor`
    Then the CLI should create `.cliplin/config.yaml` with proper configuration
    And the CLI should create `README.md` if it doesn't exist
    And the CLI should include the AI tool configuration in the config file
    And the CLI should display success messages for each created file

  Scenario: Handle invalid AI tool ID
    Given I have the Cliplin CLI tool installed
    And I am in an empty directory or a new project directory
    When I run `cliplin init --ai invalid-tool`
    Then the CLI should display an error message indicating that the AI tool ID is not recognized
    And the CLI should list available AI tool IDs (e.g., "cursor", "claude-desktop")
    And the CLI should exit with a non-zero status code
    And no files should be created in the current directory

  Scenario: Display help information
    Given I have the Cliplin CLI tool installed
    When I run `cliplin --help`
    Then the CLI should display usage information
    And the CLI should list all available commands (init, validate, reindex, etc.)
    And the CLI should show command options and arguments
    And the CLI should display examples of command usage
    And the CLI should show the `reindex` command with its options:
      | Option | Description |
      | --type | Reindex files of a specific type (ts4, feature, md, yaml) |
      | --directory | Reindex all files in a specific directory |
      | --dry-run | Review changes without reindexing |
      | --verbose | Display detailed output |
      | --interactive | Prompt for confirmation before reindexing |

  Scenario: Display version information
    Given I have the Cliplin CLI tool installed
    When I run `cliplin --version`
    Then the CLI should display the version number
    And the CLI should display the Python version being used
    And the CLI should display the uv version if available

  Scenario: Reindex all context files
    Given I have initialized a Cliplin project using `cliplin init --ai cursor`
    And the ChromaDB database exists at `.cliplin/data/context/chroma.sqlite3`
    And there are context files in the project directories
    When I run `cliplin reindex`
    Then the CLI should scan for context files in the following directories:
      | Directory | File Pattern | Collection |
      | docs/adrs | *.md | business-and-architecture |
      | docs/business | *.md | business-and-architecture |
      | docs/features | *.feature | features |
      | docs/ts4 | *.ts4 | tech-specs |
      | docs/ui-intent | *.yaml | uisi |
    And the CLI should check if each file already exists in ChromaDB by file path
    And for each file that exists, the CLI should update it in ChromaDB
    And for each file that does not exist, the CLI should add it to ChromaDB
    And the CLI should include proper metadata for each document:
      | Metadata Field | Description |
      | file_path | Relative path to file from project root |
      | type | File type (ts4, adr, project-doc, feature, ui-intent) |
      | collection | Target collection name |
    And the CLI should use the file path as the document ID
    And the CLI should display a summary of reindexing results:
      | Files Added | Files Updated | Files Skipped | Errors |
    And the CLI should display success message indicating reindexing is complete

  Scenario: Reindex specific context file
    Given I have initialized a Cliplin project using `cliplin init --ai cursor`
    And the ChromaDB database exists at `.cliplin/data/context/chroma.sqlite3`
    And there is a file `docs/ts4/my-spec.ts4` in the project
    When I run `cliplin reindex docs/ts4/my-spec.ts4`
    Then the CLI should validate that the file exists
    And the CLI should determine the target collection based on file type and location:
      | File Path | Collection |
      | docs/ts4/*.ts4 | tech-specs |
      | docs/adrs/*.md | business-and-architecture |
      | docs/business/*.md | business-and-architecture |
      | docs/features/*.feature | features |
      | docs/ui-intent/*.yaml | uisi |
    And the CLI should check if the file already exists in ChromaDB
    And if the file exists, the CLI should update it with new content
    And if the file does not exist, the CLI should add it to ChromaDB
    And the CLI should include proper metadata with file_path, type, and collection
    And the CLI should display a success message indicating the file was reindexed

  Scenario: Reindex all files of a specific type (TS4)
    Given I have initialized a Cliplin project using `cliplin init --ai cursor`
    And the ChromaDB database exists at `.cliplin/data/context/chroma.sqlite3`
    And there are multiple `.ts4` files in `docs/ts4/` directory
    When I run `cliplin reindex --type ts4`
    Then the CLI should scan for all `.ts4` files in `docs/ts4/` directory
    And the CLI should reindex each `.ts4` file to the `tech-specs` collection
    And the CLI should process each file with proper metadata
    And the CLI should display a summary showing how many TS4 files were reindexed

  Scenario: Reindex all files of a specific type (features)
    Given I have initialized a Cliplin project using `cliplin init --ai cursor`
    And the ChromaDB database exists at `.cliplin/data/context/chroma.sqlite3`
    And there are multiple `.feature` files in `docs/features/` directory
    When I run `cliplin reindex --type feature`
    Then the CLI should scan for all `.feature` files in `docs/features/` directory
    And the CLI should reindex each `.feature` file to the `features` collection
    And the CLI should process each file with proper metadata
    And the CLI should display a summary showing how many feature files were reindexed

  Scenario: Reindex all files in a specific directory
    Given I have initialized a Cliplin project using `cliplin init --ai cursor`
    And the ChromaDB database exists at `.cliplin/data/context/chroma.sqlite3`
    And there are multiple files in `docs/business/` directory
    When I run `cliplin reindex --directory docs/business`
    Then the CLI should scan for all `.md` files in `docs/business/` directory
    And the CLI should reindex each file to the `business-and-architecture` collection
    And the CLI should determine the correct collection based on directory:
      | Directory | Collection |
      | docs/adrs | business-and-architecture |
      | docs/business | business-and-architecture |
      | docs/features | features |
      | docs/ts4 | tech-specs |
      | docs/ui-intent | uisi |
    And the CLI should process each file with proper metadata
    And the CLI should display a summary showing how many files were reindexed

  Scenario: Review changes in context files without reindexing
    Given I have initialized a Cliplin project using `cliplin init --ai cursor`
    And the ChromaDB database exists at `.cliplin/data/context/chroma.sqlite3`
    And there are context files in the project
    When I run `cliplin reindex --dry-run`
    Then the CLI should scan for context files in all context directories
    And the CLI should check which files exist in ChromaDB
    And the CLI should detect which files have been modified since last indexing
    And the CLI should display a report showing:
      | File Path | Status | Action |
      | docs/ts4/new-file.ts4 | New | Would add |
      | docs/ts4/existing-file.ts4 | Modified | Would update |
      | docs/ts4/unchanged-file.ts4 | Unchanged | Would skip |
    And the CLI should not make any changes to ChromaDB
    And the CLI should display a summary of what would be reindexed

  Scenario: Handle reindexing when ChromaDB is not initialized
    Given I have initialized a Cliplin project using `cliplin init --ai cursor`
    And the ChromaDB database does not exist at `.cliplin/data/context/chroma.sqlite3`
    When I run `cliplin reindex`
    Then the CLI should detect that ChromaDB is not initialized
    And the CLI should display an error message indicating that ChromaDB must be initialized first
    And the CLI should suggest running `cliplin init` to initialize the project
    And the CLI should exit with a non-zero status code

  Scenario: Handle reindexing when file does not exist
    Given I have initialized a Cliplin project using `cliplin init --ai cursor`
    And the ChromaDB database exists at `.cliplin/data/context/chroma.sqlite3`
    When I run `cliplin reindex docs/ts4/non-existent-file.ts4`
    Then the CLI should validate that the file exists
    And the CLI should display an error message indicating that the file does not exist
    And the CLI should exit with a non-zero status code
    And no changes should be made to ChromaDB

  Scenario: Handle reindexing file outside context directories
    Given I have initialized a Cliplin project using `cliplin init --ai cursor`
    And the ChromaDB database exists at `.cliplin/data/context/chroma.sqlite3`
    And there is a file `src/main.py` in the project
    When I run `cliplin reindex src/main.py`
    Then the CLI should validate that the file is in a context directory
    And the CLI should display an error message indicating that the file is not in a valid context directory
    And the CLI should list valid context directories:
      | docs/adrs |
      | docs/business |
      | docs/features |
      | docs/ts4 |
      | docs/ui-intent |
    And the CLI should exit with a non-zero status code

  Scenario: Reindex with verbose output
    Given I have initialized a Cliplin project using `cliplin init --ai cursor`
    And the ChromaDB database exists at `.cliplin/data/context/chroma.sqlite3`
    And there are context files in the project
    When I run `cliplin reindex --verbose`
    Then the CLI should display detailed information for each file being processed:
      | File Path | Collection | Action | Status |
    And the CLI should display metadata being added for each file
    And the CLI should display any warnings or errors encountered during processing
    And the CLI should provide progress indicators for large batches of files

  Scenario: Reindex with confirmation prompt
    Given I have initialized a Cliplin project using `cliplin init --ai cursor`
    And the ChromaDB database exists at `.cliplin/data/context/chroma.sqlite3`
    And there are context files in the project
    When I run `cliplin reindex --interactive`
    Then the CLI should scan for context files
    And the CLI should display a list of files that will be reindexed
    And the CLI should prompt for confirmation: "Reindex X files? (y/n)"
    And if the user confirms (y/yes), the CLI should proceed with reindexing
    And if the user declines (n/no), the CLI should abort without making changes
    And the CLI should display a message indicating the action taken

  Scenario: Reindex and handle duplicate documents
    Given I have initialized a Cliplin project using `cliplin init --ai cursor`
    And the ChromaDB database exists at `.cliplin/data/context/chroma.sqlite3`
    And a file `docs/ts4/test.ts4` already exists in ChromaDB with the same file path ID
    When I run `cliplin reindex docs/ts4/test.ts4`
    Then the CLI should detect that the document already exists in ChromaDB
    And the CLI should update the existing document instead of creating a duplicate
    And the CLI should use `chroma_update_documents` instead of `chroma_add_documents`
    And the CLI should update the document content, metadata, and embeddings
    And the CLI should display a message indicating the file was updated

  Scenario: Reindex with collection validation
    Given I have initialized a Cliplin project using `cliplin init --ai cursor`
    And the ChromaDB database exists at `.cliplin/data/context/chroma.sqlite3`
    And all required collections exist in ChromaDB
    When I run `cliplin reindex`
    Then the CLI should verify that all required collections exist:
      | business-and-architecture |
      | features |
      | tech-specs |
      | uisi |
    And if any collection is missing, the CLI should create it before reindexing
    And the CLI should use the correct collection for each file type
    And the CLI should display an error if it cannot access or create a collection

