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
    
    readme_path.write_text(readme_content, encoding="utf-8")
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
    
    adr_path.write_text(adr_content, encoding="utf-8")
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
    
    adr_path.write_text(adr_content, encoding="utf-8")
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
    
    adr_path.write_text(adr_content, encoding="utf-8")
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
        context_file.write_text(context_content, encoding="utf-8")
        console.print(f"  [green]✓[/green] Created {config['config_file']}")
    
    # Create feature-processing.mdc for Cursor
    if ai_tool == "cursor" and config["feature_processing_file"]:
        feature_file = target_dir / config["feature_processing_file"]
        feature_content = get_cursor_feature_processing_content()
        feature_file.write_text(feature_content, encoding="utf-8")
        console.print(f"  [green]✓[/green] Created {config['feature_processing_file']}")


def create_cursor_mcp_config(target_dir: Path) -> None:
    """Create or update .cursor/mcp.json with ChromaDB MCP server configuration."""
    mcp_file = target_dir / ".cursor" / "mcp.json"
    mcp_file.parent.mkdir(parents=True, exist_ok=True)
    
    # ChromaDB database path relative to project root
    chromadb_path = ".cliplin/data/context"
    
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

## MANDATORY: Load Context Before Any Task

**CRITICAL RULE**: Before starting ANY planning, coding, or thinking task, you MUST:

1. **Load context from ChromaDB MCP server**: Use the 'cliplin-context' MCP server (ChromaDB MCP server) as the source of truth
2. **Query relevant collections**: Use ChromaDB MCP tools (chroma_query_documents) to query and load relevant context from the appropriate collections:
   - 'business-and-architecture' collection: ADRs and business documentation md files located at 'docs/adrs' and 'docs/business' folder
   - 'features' collection: .feature files located at 'docs/features' folder
   - 'tech-specs' collection: .ts4 files located at 'docs/ts4' folder
   - 'uisi' collection: .yaml files located at 'docs/ui-intent' folder
3. **Never proceed without context**: Do NOT start any task until you have queried and loaded the relevant context from ChromaDB collections
4. **Use semantic queries**: Query collections using semantic search based on the task domain, entities, and requirements to retrieve the most relevant context
   
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

0. **Context Loading Phase (MANDATORY FIRST STEP)**:
   - **CRITICAL**: Before starting ANY feature analysis or implementation, you MUST load context from the ChromaDB MCP server 'cliplin-context'
   - **Use MCP tools to query collections**: Use the ChromaDB MCP tools (chroma_query_documents) to load relevant context from ALL collections:
     * Query `business-and-architecture` collection to load ADRs and business documentation
     * Query `tech-specs` collection to load technical specifications and implementation rules
     * Query `features` collection to load related or dependent features
     * Query `uisi` collection to load UI/UX requirements if applicable
   - **Query strategy**: Use semantic queries based on the feature domain, entities, and use cases to retrieve relevant context
   - **Never proceed without loading context**: Do NOT start feature analysis or implementation until you have queried and loaded the relevant context from ChromaDB
   - **Context update check**: After loading context, verify if any context files need reindexing:
     * Run `cliplin reindex --dry-run` to check if context files are up to date
     * If context files are outdated, ask user for confirmation before reindexing
     * Only proceed with feature work after ensuring context is current and loaded

1. **Feature Analysis Phase**:
   - Read and analyze the `.feature` file from the `docs/features/` directory
   - Identify all scenarios (Given-When-Then steps)
   - **Analyze scenario status tags**: For each scenario, identify its current status based on tags:
     * `@status:new` - New scenario that needs implementation
     * `@status:pending` - Scenario pending implementation
     * `@status:implemented` - Scenario fully implemented and working
     * `@status:deprecated` - Scenario deprecated, should not be updated, only maintained
     * `@status:modified` - Scenario that has been modified and may need re-implementation
     * `@changed:YYYY-MM-DD` - Date when scenario was last changed
     * `@reason:<description>` - Reason for status change or modification
   - **Filter scenarios by status**: Only work on scenarios that are NOT deprecated:
     * Skip scenarios tagged with `@status:deprecated` during implementation
     * Focus on scenarios with `@status:new`, `@status:pending`, or `@status:modified`
     * Maintain deprecated scenarios as-is without modifications
   - Extract business rules and acceptance criteria
   - Identify domain entities, use cases, and boundaries
   - **Use loaded context**: Apply the context loaded from ChromaDB in phase 0 to inform your analysis:
     * Use business rules from `business-and-architecture` collection
     * Apply technical constraints from `tech-specs` collection
     * Consider dependencies from related features in `features` collection
     * Incorporate UI/UX requirements from `uisi` collection if applicable

2. **Detailed Implementation Plan Creation**:
   Create a comprehensive plan that includes:
   
   **a) Architecture Analysis**:
   - **Use loaded context**: Apply the context already loaded from ChromaDB in phase 0
   - Use ADRs from `business-and-architecture` collection to understand existing architecture decisions
   - Apply technical constraints and patterns from `tech-specs` collection
   - Identify which domain layer components are needed (entities, value objects, use cases)
   - Determine required ports (interfaces) following hexagonal architecture
   - Identify adapters needed (repositories, external services, etc.)
   - Map feature scenarios to use cases
   - Ensure consistency with existing patterns documented in the loaded context
   - If additional context is needed, query ChromaDB collections again with more specific queries
   
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
   - Map each active scenario (non-deprecated) from the `.feature` file to BDD test steps
   - Implement step definitions that exercise the full feature flow
   - Ensure BDD tests validate end-to-end feature behavior
   - BDD tests should use real adapters (not mocks) to validate integration
   - **Exclude deprecated scenarios**: Do not create or update BDD tests for scenarios tagged with `@status:deprecated`
   
   **e) Implementation Checklist**:
   - [ ] Domain entities and value objects
   - [ ] Use case implementations
   - [ ] Unit tests for business logic
   - [ ] BDD/acceptance tests
   - [ ] Error handling and validation
   - [ ] Type hints and documentation

3. **Implementation Execution**:
   - Follow the plan step by step
   - **Work on active scenarios only**: Implement only scenarios that are NOT deprecated
   - Implement domain logic first
   - Write unit tests alongside business logic implementation (TDD approach)
   - Write BDD tests that validate the active scenarios (non-deprecated)
   - Ensure all tests pass before marking scenarios as complete

4. **Feature Completion**:
   - Once implementation is complete and tests pass for a scenario:
     * **Add scenario-level tags**: Add tags directly above each scenario (not at feature level):
       - `@status:implemented` - When a scenario is fully implemented and tested
       - `@status:new` - When creating a new scenario (remove after implementation)
       - `@status:modified` - When modifying an existing scenario (remove after re-implementation)
       - `@changed:YYYY-MM-DD` - Date when scenario was last changed
       - `@reason:<description>` - Optional reason for status change
     * **Tag format example**:
       ```
       @status:implemented
       @changed:2024-01-15
       Scenario: Example scenario name
         Given ...
       ```
     * **Do NOT modify deprecated scenarios**: Leave scenarios with `@status:deprecated` unchanged
     * Ensure the feature file is properly formatted and readable
     * All code and tests must be traceable back to the specific scenarios
     * **Reindex the updated feature file**: Run `cliplin reindex docs/features/feature-name.feature` to update ChromaDB
     * If you created or modified any context files (ADRs, TS4, business docs), reindex them as well
     * This ensures the context remains synchronized with the implementation

### When User Requests Feature Modification

When a user asks to modify an existing feature:

0. **Context Loading Phase (MANDATORY FIRST STEP)**:
   - **CRITICAL**: Before starting ANY feature modification analysis, you MUST load context from the ChromaDB MCP server 'cliplin-context'
   - **Use MCP tools to query collections**: Use the ChromaDB MCP tools (chroma_query_documents) to load relevant context:
     * Query `features` collection to load the feature being modified and related features that might be affected
     * Query `business-and-architecture` collection to load business rules and ADRs that might impact the change
     * Query `tech-specs` collection to load technical constraints that must be considered
     * Query `uisi` collection if UI/UX changes are involved
   - **Query strategy**: Use semantic queries based on the feature domain, entities, and use cases to retrieve relevant context
   - **Never proceed without loading context**: Do NOT start modification analysis until you have queried and loaded the relevant context from ChromaDB
   - **Context update check**: After loading context, verify if any context files need reindexing:
     * Run `cliplin reindex --dry-run` to check if context files are up to date
     * If context files are outdated, ask user for confirmation before reindexing
     * Only proceed with feature modification after ensuring context is current and loaded

1. **Impact Analysis**:
   - **Use loaded context**: Apply the context already loaded from ChromaDB in phase 0
   - **Identify scenarios to modify**: Analyze which specific scenarios need changes:
     * Review scenario tags to understand current status
     * Identify scenarios tagged with `@status:modified` or scenarios that need modification
     * **Exclude deprecated scenarios**: Do not modify scenarios tagged with `@status:deprecated`
   - Identify all features, components, and context files that depend on or relate to the scenarios being modified
   - Analyze the scope of changes required based on the loaded context
   - Check for breaking changes that might affect other features using the loaded feature dependencies
   - If additional context is needed, query ChromaDB collections again with more specific queries

2. **Modification Process**:
   - Follow the same phases as feature implementation (Analysis, Planning, Implementation, Completion)
   - **Work on specific scenarios**: Only modify the scenarios that need changes, not the entire feature
   - Ensure backward compatibility unless explicitly breaking changes are required
   - Update related context files if business rules or technical specs change
   - **Update scenario tags**: When modifying a scenario:
     * If modifying an existing implemented scenario, add `@status:modified` tag
     * Add `@changed:YYYY-MM-DD` tag with the modification date
     * Add `@reason:<description>` tag explaining why the scenario was modified
     * After re-implementation, change `@status:modified` to `@status:implemented`
     * **Example**:
       ```
       @status:modified
       @changed:2024-01-15
       @reason:Updated to support new authentication flow
       Scenario: User login
         Given ...
       ```
   - **Deprecate scenarios if needed**: If a scenario should no longer be updated:
     * Add `@status:deprecated` tag to the scenario
     * Add `@changed:YYYY-MM-DD` and `@reason:<description>` tags
     * Keep the scenario in the file for reference but do not modify it further

3. **Post-Modification**:
   - Reindex all modified context files using `cliplin reindex`
   - Verify that related features still work correctly
   - **Verify scenario status**: Ensure all modified scenarios have appropriate tags:
     * Implemented scenarios should have `@status:implemented`
     * Deprecated scenarios should have `@status:deprecated` and should not be modified
     * Modified scenarios should be updated to `@status:implemented` after completion
   - Update documentation if needed

### Scenario Status Tags Reference

When working with feature files, use the following tags at the **scenario level** (not feature level):

- **`@status:new`** - New scenario that needs implementation. Remove this tag after implementation.
- **`@status:pending`** - Scenario pending implementation. Default status for new scenarios.
- **`@status:implemented`** - Scenario fully implemented, tested, and working.
- **`@status:deprecated`** - Scenario deprecated. Should NOT be updated or modified, only maintained for reference.
- **`@status:modified`** - Scenario that has been modified and may need re-implementation. Change to `@status:implemented` after completion.
- **`@changed:YYYY-MM-DD`** - Date when scenario was last changed (format: YYYY-MM-DD).
- **`@reason:<description>`** - Optional reason for status change or modification.

**Tag placement**: Tags should be placed directly above the `Scenario:` line:
```
@status:implemented
@changed:2024-01-15
@reason:Updated authentication flow
Scenario: User login with OAuth
  Given ...
```

**Important rules**:
- Tags are **scenario-specific**, not feature-level
- **Never modify** scenarios tagged with `@status:deprecated`
- Always update `@changed` and `@status` tags when modifying scenarios
- Use `@reason` tag to document why changes were made
"""

