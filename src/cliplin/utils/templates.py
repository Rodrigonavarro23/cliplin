"""Template management utilities."""

import json
from pathlib import Path
from typing import Dict, Optional

from rich.console import Console

console = Console()

# AI tool configurations
AI_TOOL_CONFIGS: Dict[str, Dict[str, str]] = {
    "cursor": {
        "rules_dir": ".cursor/rules",
        "config_file": ".cursor/rules/context.mdc",
        "feature_processing_file": ".cursor/rules/feature-processing.mdc",
    },
    "claude-desktop": {
        "rules_dir": ".claude",
        "config_file": ".claude/mcp_config.json",
        "feature_processing_file": None,
    },
}


def create_config_file(target_dir: Path, ai_tool: Optional[str] = None) -> None:
    """Create the Cliplin configuration file."""
    config_path = target_dir / ".cliplin" / "config.yaml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    config_content = """# Cliplin Project Configuration

version: "1.0"
project_name: ""

# ChromaDB Configuration
chromadb:
  path: ".cliplin/data/context/chroma.sqlite3"
  collections:
    - business-and-architecture
    - features
    - tech-specs
    - uisi

# AI Tool Configuration
"""
    if ai_tool:
        config_content += f"ai_tool: {ai_tool}  # Set when using cliplin init --ai\n"
    else:
        config_content += "ai_tool: null  # Set to 'cursor' or 'claude-desktop' when using cliplin init --ai\n"
    
    config_path.write_text(config_content)
    console.print(f"  [green]✓[/green] Created .cliplin/config.yaml")


def create_readme_file(target_dir: Path) -> None:
    """Create a basic README file for the Cliplin project."""
    readme_path = target_dir / "README.md"
    
    # Only create if it doesn't exist
    if readme_path.exists():
        console.print(f"  [yellow]⚠[/yellow]  README.md already exists, skipping")
        return
    
    readme_content = """# Cliplin Project

This project uses Cliplin for AI-assisted development driven by specifications.

## Directory Structure

- `docs/adrs/` - Architecture Decision Records
- `docs/business/` - Business documentation
- `docs/features/` - Feature files (Gherkin)
- `docs/ts4/` - Technical specifications
- `docs/ui-intent/` - UI Intent specifications

## Getting Started

1. Add your feature files to `docs/features/`
2. Add your TS4 specifications to `docs/ts4/`
3. Add your business documentation to `docs/business/`
4. Run `cliplin reindex` to index your context files
"""
    
    readme_path.write_text(readme_content)
    console.print(f"  [green]✓[/green] Created README.md")


def create_framework_adr(target_dir: Path) -> None:
    """Create ADR about the Cliplin Framework."""
    adr_path = target_dir / "docs" / "adrs" / "000-cliplin-framework.md"
    adr_path.parent.mkdir(parents=True, exist_ok=True)
    
    adr_content = """# ADR-000: Cliplin Framework Overview

## Status
Accepted

## Context

This project uses the **Cliplin Framework** for AI-assisted development driven by specifications. This ADR provides essential context about the framework so that AI assistants understand the operational model and specification types available.

## Decision

### Core Principle (Kidlin's Law)
> **Describe the problem clearly, and half of it is already solved.**

Cliplin operationalizes this by enforcing that **AI is only allowed to act on well-defined, versioned specifications that live in the repository**. Code becomes an output of the system — not its source of truth.

### The Four Pillars of Cliplin

Cliplin is built on four complementary specification pillars, each with a precise responsibility:

#### 1. Business Features (.feature files – Gherkin)
- **Purpose**: Define *what* the system must do and *why*
- **Location**: `docs/features/*.feature`
- **Format**: Gherkin syntax with Given-When-Then scenarios
- **Key principle**: If a feature does not exist, the functionality does not exist
- **Tags**: 
  - `@status:pending` or no tag = not implemented
  - `@status:implemented` = implemented and active
  - `@status:deprecated` = must not be modified
  - `@changed:YYYY-MM-DD` = change tracking
  - `@reason:<description>` = change justification
- **Role**: Features orchestrate execution and represent the source of truth

#### 2. UI Intent Specifications (YAML)
- **Purpose**: Define *how the system expresses intent to users*, beyond visual design
- **Location**: `docs/ui-intent/*.yaml`
- **Focus**: Semantic meaning, layout relationships, intent preservation, state-driven behavior
- **Schema sections**: structure, semantics, state_model, motion, constraints, annotations
- **Key principle**: Emphasizes semantic meaning over visual appearance
- **Usage**: Allows AI to generate UI code without guessing user experience decisions

#### 3. TS4 – Technical Specification Files (YAML)
- **Purpose**: Define *how software must be implemented*
- **Location**: `docs/ts4/*.ts4`
- **Key principle**: TS4 does not describe what to build. It defines how to build it correctly.
- **Contains**: Coding conventions, naming rules, validation strategies, allowed/forbidden patterns, project-specific technical decisions
- **Format**: YAML with `ts4`, `id` (kebab-case), `title`, `summary`, `rules[]`, optional `code_refs[]`
- **Role**: Acts as a technical contract for implementation

#### 4. Architecture Decision Records and Business Documentation (ADRs and .md files)
- **Purpose**: Preserve *why technical decisions were made*
- **Locations**: `docs/adrs/*.md`, `docs/business/*.md`
- **Contains**: Architecture choices, trade-offs, constraints, business descriptions, environment considerations
- **Role**: Prevents AI (and humans) from reopening closed decisions or proposing invalid architectures

### Cliplin as an Operational Model

**Valid Inputs Only:**
- Business Features (.feature in docs/features/)
- UI Intent specifications (.yaml in docs/ui-intent/)
- TS4 technical rules (.ts4 in docs/ts4/)
- ADRs and business documentation (.md in docs/adrs/ and docs/business/)

**Everything else is noise.** All outputs must be traceable back to a specification.

### Constraints

Cliplin works by **deliberate limitation**:
- Business constraints (Features)
- Semantic constraints (UI Intent)
- Technical constraints (TS4)
- Architectural constraints (ADRs)

Creativity is replaced by clarity.

### Outputs

Expected outputs are:
- Business-aligned code
- Tests derived from scenarios
- UI consistent with intent
- Architecture-compliant changes

Every output must be traceable back to a specification.

## Consequences

### Positive
- Reduced ambiguity in AI-assisted development
- Predictable AI behavior based on specifications
- Clear separation of concerns across specification types
- Versionable and maintainable specifications
- All context available through ChromaDB indexing

### Notes
- This ADR should be indexed in ChromaDB collection `business-and-architecture`
- AI assistants should query this ADR and related context files before starting any work
- All specifications must be kept up to date and properly indexed
"""
    
    adr_path.write_text(adr_content)
    console.print(f"  [green]✓[/green] Created docs/adrs/000-cliplin-framework.md")


def create_ts4_format_adr(target_dir: Path) -> None:
    """Create ADR about TS4 format and usage."""
    adr_path = target_dir / "docs" / "adrs" / "001-ts4-format.md"
    adr_path.parent.mkdir(parents=True, exist_ok=True)
    
    adr_content = """# ADR-001: TS4 Format and Usage

## Status
Accepted

## Context

TS4 (Technical Specs for AI) is a lightweight, human-readable format for documenting technical decisions, implementation rules, and code references. This ADR explains the TS4 format so that AI assistants can understand and work with TS4 files correctly.

## Decision

### What is TS4?

TS4 is a YAML-based format optimized for AI indexing and retrieval. Each TS4 file contains technical decisions, implementation rules, and code references in a compact, maintainable format.

### TS4 File Structure

A typical TS4 file has the following structure:

```yaml
ts4: "1.0"
id: "system-input-validation"  # kebab-case identifier
title: "System Input Validations"
summary: "Validate data at controllers; internal services assume data validity."
rules:
  - "Avoid repeating validations in internal services"
  - "Provide clear errors with 4xx HTTP status codes"
code_refs:  # Optional
  - "handlers/user.go"
  - "pkg/validation/*.go"
```

### Field Descriptions

- **ts4**: Version of the TS4 format (currently "1.0")
- **id**: Unique identifier in kebab-case format (lowercase words separated by hyphens)
- **title**: Descriptive title of the technical specification
- **summary**: Brief summary of what this specification covers
- **rules**: Array of implementation rules or guidelines (strings)
- **code_refs**: Optional array of file paths or patterns related to this specification

### Key Principles

1. **TS4 does not describe what to build. It defines how to build it correctly.**
2. TS4 files act as a **technical contract** for implementation
3. Each TS4 file should focus on a specific technical decision or set of related rules
4. The `id` field should be descriptive and use kebab-case (e.g., "system-input-validation")

### Benefits

- **Live Context for AI**: Embedding-friendly, ideal for RAG and LangChain
- **Technical Traceability**: Clear and accessible rules without noise
- **Versionable and Incremental**: Designed for Git and continuous evolution
- **AI-Ready, Dev-Friendly**: Uses YAML without unnecessary complexity

### Usage

- TS4 files are located in `docs/ts4/` directory
- They are indexed in ChromaDB collection `tech-specs`
- AI assistants should query `tech-specs` collection before implementation to understand technical constraints
- TS4 files complement ADRs: ADRs explain *why*, TS4 files define *how*

## Consequences

### Positive
- Clear technical constraints for AI assistants
- Easy to maintain and update
- Optimized for AI context retrieval
- Supports incremental documentation

### Notes
- This ADR should be indexed in ChromaDB collection `business-and-architecture`
- When creating new TS4 files, follow the structure and naming conventions described here
"""
    
    adr_path.write_text(adr_content)
    console.print(f"  [green]✓[/green] Created docs/adrs/001-ts4-format.md")


def create_ui_intent_format_adr(target_dir: Path) -> None:
    """Create ADR about UI Intent format and usage."""
    adr_path = target_dir / "docs" / "adrs" / "002-ui-intent-format.md"
    adr_path.parent.mkdir(parents=True, exist_ok=True)
    
    adr_content = """# ADR-002: UI Intent Schema Format and Usage

## Status
Accepted

## Context

The **UI Intent Schema** is a declarative YAML format designed to describe user interfaces with **preserved semantic intent**. This ADR explains the UI Intent format so that AI assistants can understand and work with UI Intent files correctly.

## Decision

### What is UI Intent?

UI Intent specifications describe user interfaces with preserved semantic intent. Unlike visual design tools that focus on pixel-perfect positioning, this schema emphasizes:
- **Semantic meaning** over visual appearance
- **Layout relationships** over absolute coordinates
- **Intent preservation** across different render contexts
- **State-driven behavior** rather than timeline animations

### UI Intent Schema Structure

The UI Intent specification consists of five main sections:

```yaml
structure:          # Component hierarchy and layout
semantics:          # Meaning and accessibility information
state_model:        # Interactive states and transitions
motion:             # State-driven visual effects
constraints:        # Behavioral rules
annotations:        # Design rationale and notes (optional)
```

### Structure Section

Defines component hierarchy and layout:

```yaml
structure:
  components:
    - id: string                    # Unique identifier (required)
      type: NodeType                # Component type (required)
      layout: LayoutSpec            # Layout specification (required)
      children?: string[]           # Array of child component IDs (optional)
      content?: string              # Text content (optional)
      attributes?: Record<string, any>  # HTML attributes (optional)
```

**Component Types**: container, text, input, textarea, select, button, checkbox, radio, label, icon, image, link (can be extended with design system components)

**Layout Specification**:
- `anchor`: top, bottom, left, right, center, fill
- `width`, `height`: pixels, percentages, viewport units (vw/vh), "fill"
- `x`, `y`: coordinates (relative to parent or absolute)
- `padding`, `margin`: spacing specifications
- `zIndex`: stacking order

### Semantics Section

Provides accessibility and meaning information:

```yaml
semantics:
  component_id:
    role?: string           # Semantic role (e.g., "primary_action")
    label?: string          # Human-readable label
    ariaLabel?: string      # ARIA label for screen readers
    description?: string    # Extended description
```

### State Model Section

Defines interactive states and transitions:

```yaml
state_model:
  states: string[]              # List of possible states
  currentState: string          # Currently active state
  transitions?:                 # State transitions (optional)
    - from: string
      to: string
      on: string                # Trigger event (e.g., "click")
```

### Motion Section

Defines visual effects for each state:

```yaml
motion:
  state_name:
    component_id:
      opacity?: number
      borderEmphasis?: boolean
      scale?: number
      translateX?: number
      translateY?: number
      animation?: string        # Design system animation preset
```

**Note**: Motion is **state-driven**, not timeline-based.

### Constraints Section

Defines behavioral rules:

```yaml
constraints:
  - id: string
    target: string              # Component ID
    type: ConstraintType       # visibility, position, size, relationship
    condition: string
    value?: any
```

### Annotations Section

Captures design rationale and notes:

```yaml
annotations:
  - id: string
    target: string
    type: AnnotationType       # rationale, note, constraint, todo
    content: string
    position?: { x: number, y: number }
    visible?: boolean
```

### Key Principles

1. **Preserve semantic intent**, not pixel-perfect positioning
2. **Use anchors and relative positioning** for responsive layouts
3. **Separate structure from semantics**
4. **State-driven motion** (not timeline-based)
5. **Leverage design system components** when available

### Usage

- UI Intent files are located in `docs/ui-intent/` directory
- They are indexed in ChromaDB collection `uisi`
- AI assistants should query `uisi` collection when implementing user interfaces
- UI Intent allows AI to generate UI code without guessing user experience decisions

## Consequences

### Positive
- Clear UI/UX specifications for AI assistants
- Semantic intent preserved across render contexts
- Supports design system integration
- Optimized for AI context retrieval

### Notes
- This ADR should be indexed in ChromaDB collection `business-and-architecture`
- When creating new UI Intent files, follow the schema structure described here
- UI Intent focuses on intent, not visual design details
"""
    
    adr_path.write_text(adr_content)
    console.print(f"  [green]✓[/green] Created docs/adrs/002-ui-intent-format.md")


def create_ai_tool_config(target_dir: Path, ai_tool: str) -> None:
    """Create AI tool-specific configuration files."""
    if ai_tool not in AI_TOOL_CONFIGS:
        raise ValueError(f"Unknown AI tool: {ai_tool}")
    
    config = AI_TOOL_CONFIGS[ai_tool]
    rules_dir = target_dir / config["rules_dir"]
    rules_dir.mkdir(parents=True, exist_ok=True)
    
    # Create MCP configuration files
    if ai_tool == "cursor":
        create_cursor_mcp_config(target_dir)
    elif ai_tool == "claude-desktop":
        create_claude_desktop_mcp_config(target_dir)
    
    # Create context.mdc for Cursor
    if ai_tool == "cursor" and config["config_file"]:
        context_file = target_dir / config["config_file"]
        context_content = get_cursor_context_content()
        context_file.write_text(context_content)
        console.print(f"  [green]✓[/green] Created {config['config_file']}")
    
    # Create feature-processing.mdc for Cursor
    if ai_tool == "cursor" and config["feature_processing_file"]:
        feature_file = target_dir / config["feature_processing_file"]
        feature_content = get_cursor_feature_processing_content()
        feature_file.write_text(feature_content)
        console.print(f"  [green]✓[/green] Created {config['feature_processing_file']}")


def create_cursor_mcp_config(target_dir: Path) -> None:
    """Create or update .cursor/mcp.json with ChromaDB MCP server configuration."""
    mcp_file = target_dir / ".cursor" / "mcp.json"
    mcp_file.parent.mkdir(parents=True, exist_ok=True)
    
    # ChromaDB database path relative to project root
    chromadb_path = ".cliplin/data/context/chroma.sqlite3"
    
    # MCP server configuration
    cliplin_server_config = {
        "command": "uvx",
        "args": [
            "chroma-mcp",
            "--client-type",
            "persistent",
            "--data-dir",
            chromadb_path
        ]
    }
    
    # Read existing config if it exists
    existing_config = {}
    if mcp_file.exists():
        try:
            with open(mcp_file, "r", encoding="utf-8") as f:
                existing_config = json.load(f)
        except (json.JSONDecodeError, IOError):
            # If file is corrupted or unreadable, start fresh
            existing_config = {}
    
    # Initialize mcpServers if it doesn't exist
    if "mcpServers" not in existing_config:
        existing_config["mcpServers"] = {}
    
    # Check if cliplin-context server already exists
    if "cliplin-context" in existing_config["mcpServers"]:
        # Update existing configuration
        existing_config["mcpServers"]["cliplin-context"] = cliplin_server_config
        console.print(f"  [yellow]⚠[/yellow]  Updated existing Cliplin MCP server in .cursor/mcp.json")
    else:
        # Add new server configuration
        existing_config["mcpServers"]["cliplin-context"] = cliplin_server_config
        console.print(f"  [green]✓[/green] Created .cursor/mcp.json")
    
    # Write updated configuration
    with open(mcp_file, "w", encoding="utf-8") as f:
        json.dump(existing_config, f, indent=2, ensure_ascii=False)


def create_claude_desktop_mcp_config(target_dir: Path) -> None:
    """Create or update .claude/mcp_config.json with ChromaDB MCP server configuration."""
    mcp_file = target_dir / ".claude" / "mcp_config.json"
    mcp_file.parent.mkdir(parents=True, exist_ok=True)
    
    # ChromaDB database path relative to project root
    chromadb_path = ".cliplin/data/context/chroma.sqlite3"
    
    # MCP server configuration
    cliplin_server_config = {
        "command": "uvx",
        "args": [
            "chroma-mcp",
            "--client-type",
            "persistent",
            "--data-dir",
            chromadb_path
        ]
    }
    
    # Read existing config if it exists
    existing_config = {}
    if mcp_file.exists():
        try:
            with open(mcp_file, "r", encoding="utf-8") as f:
                existing_config = json.load(f)
        except (json.JSONDecodeError, IOError):
            # If file is corrupted or unreadable, start fresh
            existing_config = {}
    
    # Initialize mcpServers if it doesn't exist
    if "mcpServers" not in existing_config:
        existing_config["mcpServers"] = {}
    
    # Check if cliplin-context server already exists
    if "cliplin-context" in existing_config["mcpServers"]:
        # Update existing configuration
        existing_config["mcpServers"]["cliplin-context"] = cliplin_server_config
        console.print(f"  [yellow]⚠[/yellow]  Updated existing Cliplin MCP server in .claude/mcp_config.json")
    else:
        # Add new server configuration
        existing_config["mcpServers"]["cliplin-context"] = cliplin_server_config
        console.print(f"  [green]✓[/green] Created .claude/mcp_config.json")
    
    # Write updated configuration
    with open(mcp_file, "w", encoding="utf-8") as f:
        json.dump(existing_config, f, indent=2, ensure_ascii=False)


def get_cursor_context_content() -> str:
    """Get the content for .cursor/rules/context.mdc"""
    return """---
alwaysApply: true
---

- Before start any planning, coding or thinking task use your internal tool called 'cliplin-context' (ChromaDB MCP server) as source of truth for rules, project guidelines, business context, architecture decision and conventions. Defined indexes or collections:
   - 'business-and-architecture' collection, store ADRs and business documentation md files located at 'docs/adrs' and 'docs/business' folder
   - 'features' collection, store .feature files located at 'docs/features' folder
   - 'tech-specs' collection, store .ts4 files located at 'docs/ts4' folder
   - 'uisi' collection, store .yaml files located at 'docs/ui-intent'
   
## Context File Indexing Rules

### File Type to Collection Mapping

The following file types should be indexed into their respective collections (see confirmation rules below):
- `.md` files in `docs/adrs/` → `business-and-architecture` collection
- `.ts4` files in `docs/ts4/` → `tech-specs` collection
- `.md` files in `docs/business/` → `business-and-architecture` collection
- `.feature` files in `docs/features/` → `features` collection
- `.yaml` files in `docs/ui-intent/` → `uisi` collection

### Metadata Requirements

- When indexing documents, always include proper metadata as an array of objects with the following structure: `[{'file_path': 'relative/path/to/file', 'type': 'ts4|adr|project-doc|feature|ui-intent', 'collection': 'target-collection-name'}]`
- Each document in the documents array must have a corresponding metadata object in the metadatas array at the same index
- Use the file path (relative to project root) as the document ID when indexing (e.g., 'docs/ts4/ts4-project-structure.ts4')
- Before indexing a document, check if it already exists by querying the collection with the file path as ID using `chroma_get_documents` or `chroma_query_documents`. If it exists, use `chroma_update_documents` to update it instead of adding a duplicate

### Automatic Detection and User Confirmation

When any context file is created or modified, you MUST:

1. **Detect the change**: Identify when files are created or modified in the following directories:
   - `.ts4` files in `docs/ts4/` → target collection: `tech-specs`
   - `.md` files in `docs/adrs/` → target collection: `business-and-architecture`
   - `.md` files in `docs/business/` → target collection: `business-and-architecture`
   - `.feature` files in `docs/features/` → target collection: `features`
   - `.yaml` files in `docs/ui-intent/` → target collection: `uisi`

2. **Always ask for confirmation**: Before indexing or re-indexing, you MUST ask the user:
   - "He detectado cambios en [archivo]. ¿Deseas reindexar este archivo en la colección [nombre-colección] para mantener el contexto actualizado?"
   - Wait for explicit user confirmation (yes/no/confirm) before proceeding
   - If the user declines, do not index the file
   - If the user confirms, proceed with indexing

3. **Indexing process** (only after user confirmation):
   - **Preferred method**: Use the Cliplin CLI command `cliplin reindex <file-path>` which handles all the complexity automatically
   - **Alternative method** (if CLI not available): Use ChromaDB MCP tools directly:
     * Check if the document already exists by querying the collection with the file path as ID using `chroma_get_documents` or `chroma_query_documents`
     * If it exists, use `chroma_update_documents` to update it
     * If it doesn't exist, use `chroma_add_documents` to add it
     * Always include proper metadata as an array of objects with the structure: `[{'file_path': 'relative/path/to/file', 'type': 'ts4|adr|project-doc|feature|ui-intent', 'collection': 'target-collection-name'}]`
     * Use the file path (relative to project root) as the document ID
     * Avoid duplicated files and outdated or deleted files in the collection

4. **Manual re-indexing requests**: When a user explicitly requests to reindex files (e.g., "reindexa los archivos en docs/business"), you should:
   - **Use the Cliplin CLI command**: Run `cliplin reindex` with appropriate options instead of manually using ChromaDB MCP tools
   - For specific files: `cliplin reindex docs/path/to/file.md`
   - For directories: `cliplin reindex --directory docs/business`
   - For file types: `cliplin reindex --type ts4`
   - For preview: `cliplin reindex --dry-run`
   - For verbose output: `cliplin reindex --verbose`
   - The CLI command handles all the complexity of checking for existing documents, updating metadata, and managing collections
   - Only use ChromaDB MCP tools directly if the CLI is not available or for specific advanced operations

5. **Automatic indexing workflow**:
   - When context files are created or modified, **prefer using the CLI command** for indexing:
     * Run `cliplin reindex <file-path>` for the specific file that was changed
     * Or run `cliplin reindex --directory <directory>` if multiple files in a directory were changed
   - The CLI ensures proper metadata, handles duplicates, and maintains consistency
   - Always ask for user confirmation before running reindex commands (unless in automated workflow)
   - Use `cliplin reindex --dry-run` first to show what would be indexed
"""


def get_cursor_feature_processing_content() -> str:
    """Get the content for .cursor/rules/feature-processing.mdc"""
    return """---
alwaysApply: true
---

## Feature File Processing Rules

### When User Requests Feature Implementation

When a user asks to implement a feature or work with `.feature` files:

0. **Context Update Phase (MANDATORY FIRST STEP)**:
   - **Before** starting any feature analysis or implementation, ensure the context is up to date
   - Run `cliplin reindex` to update all context collections in ChromaDB
   - This ensures you have access to the latest:
     * Business documentation (docs/business/*.md)
     * Architecture Decision Records (docs/adrs/*.md)
     * Technical specifications (docs/ts4/*.ts4)
     * UI Intent specifications (docs/ui-intent/*.yaml)
     * Other feature files (docs/features/*.feature)
   - If working on a specific feature file, you can reindex just that file: `cliplin reindex docs/features/feature-name.feature`
   - If working on related context files, reindex the relevant directory: `cliplin reindex --directory docs/business`
   - **Never proceed with feature implementation without ensuring context is current**
   - Use `cliplin reindex --dry-run` to preview what would be reindexed without making changes

1. **Feature Analysis Phase**:
   - Read and analyze the `.feature` file from the `docs/features/` directory
   - Identify all scenarios (Given-When-Then steps)
   - Extract business rules and acceptance criteria
   - Identify domain entities, use cases, and boundaries
   - Query ChromaDB collections to find related context:
     * Search `business-and-architecture` collection for related business rules
     * Search `tech-specs` collection for relevant technical specifications
     * Search `features` collection for related or dependent features
     * Search `uisi` collection for UI/UX requirements if applicable

2. **Detailed Implementation Plan Creation**:
   Create a comprehensive plan that includes:
   
   **a) Architecture Analysis**:
   - Use context from ChromaDB to understand existing architecture decisions
   - Query `business-and-architecture` collection for relevant ADRs
   - Query `tech-specs` collection for technical constraints and patterns
   - Identify which domain layer components are needed (entities, value objects, use cases)
   - Determine required ports (interfaces) following hexagonal architecture
   - Identify adapters needed (repositories, external services, etc.)
   - Map feature scenarios to use cases
   - Ensure consistency with existing patterns documented in context
   
   **b) Business Logic Implementation**:
   - List all business logic components to implement
   - Identify validation rules and business constraints
   - Define domain models and their relationships
   - Specify error handling requirements
   
   **c) Unit Test Strategy**:
   - For each business logic component, create unit test specifications
   - Test each use case independently with mocked dependencies
   - Test edge cases, validation rules, and error conditions
   - Use pytest fixtures for test setup
   - Mock all external dependencies using unittest.mock or pytest-mock
   - Achieve minimum 80% code coverage for business logic
   
   **d) BDD Test Strategy**:
   - Map each scenario from the `.feature` file to BDD test steps
   - Implement step definitions that exercise the full feature flow
   - Ensure BDD tests validate end-to-end feature behavior
   - BDD tests should use real adapters (not mocks) to validate integration
   
   **e) Implementation Checklist**:
   - [ ] Domain entities and value objects
   - [ ] Use case implementations
   - [ ] Unit tests for business logic
   - [ ] BDD/acceptance tests
   - [ ] Error handling and validation
   - [ ] Type hints and documentation

3. **Implementation Execution**:
   - Follow the plan step by step
   - Implement domain logic first
   - Write unit tests alongside business logic implementation (TDD approach)
   - Write BDD tests that validate the complete feature
   - Ensure all tests pass before marking feature as complete

4. **Feature Completion**:
   - Once all implementation is complete and tests pass:
     * Add `@status:implemented` tag to the feature file at the top level
     * Ensure the feature file is properly formatted and readable
     * All code and tests must be traceable back to the feature scenarios
     * **Reindex the updated feature file**: Run `cliplin reindex docs/features/feature-name.feature` to update ChromaDB
     * If you created or modified any context files (ADRs, TS4, business docs), reindex them as well
     * This ensures the context remains synchronized with the implementation

### When User Requests Feature Modification

When a user asks to modify an existing feature:

0. **Context Update Phase (MANDATORY FIRST STEP)**:
   - Run `cliplin reindex` to ensure all context is current
   - Query ChromaDB `features` collection to find related features that might be affected
   - Query `business-and-architecture` collection for business rules that might impact the change
   - Query `tech-specs` collection for technical constraints that must be considered

1. **Impact Analysis**:
   - Identify all features, components, and context files that depend on or relate to the feature being modified
   - Analyze the scope of changes required
   - Check for breaking changes that might affect other features

2. **Modification Process**:
   - Follow the same phases as feature implementation (Analysis, Planning, Implementation, Completion)
   - Ensure backward compatibility unless explicitly breaking changes are required
   - Update related context files if business rules or technical specs change
   - Add `@changed:YYYY-MM-DD` and `@reason:<description>` tags to the feature file

3. **Post-Modification**:
   - Reindex all modified context files using `cliplin reindex`
   - Verify that related features still work correctly
   - Update documentation if needed
"""

