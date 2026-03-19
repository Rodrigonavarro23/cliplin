"""Template management utilities."""

import json
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from rich.console import Console

console = Console()

def create_cliplin_config(target_dir: Path, ai_tool: Optional[str] = None) -> None:
    """Create or update cliplin.yaml at project root with optional ai_tool for validate to check MCP file."""
    config_path = target_dir / "cliplin.yaml"

    config: Dict[str, Optional[str]] = {}
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if isinstance(data, dict):
                    config = dict(data)
        except (yaml.YAMLError, IOError):
            config = {}

    if ai_tool is not None:
        config["ai_tool"] = ai_tool

    with open(config_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    if ai_tool is not None:
        console.print(f"  [green]✓[/green] Created/updated cliplin.yaml (ai_tool: {ai_tool})")
    else:
        console.print(f"  [green]✓[/green] Created cliplin.yaml")


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
- `docs/tdrs/` - Technical Decision Records (TDR)
- `docs/ui-intent/` - UI Intent specifications

## Getting Started

1. Add your feature files to `docs/features/`
2. Add your TDR specifications to `docs/tdrs/` (see `docs/business/tdr.md` for format)
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

#### 3. TDR – Technical Decision Records (Markdown, preferred)
- **Purpose**: Define *how software must be implemented* in a format compatible across AI systems
- **Location**: `docs/tdrs/*.md`
- **Key principle**: TDR does not describe what to build. It defines how to build it correctly.
- **Contains**: Same as TS4 — coding conventions, naming rules, validation strategies, allowed/forbidden patterns, project-specific technical decisions
- **Format**: Markdown with YAML frontmatter (`tdr`, `id`, `title`, `summary`), `# rules` section, optional `code_refs`; see `docs/business/tdr.md`
- **Role**: Technical contract for implementation; preferred over TS4 for new specs (Cursor, Claude, and other hosts)
- **Collection**: `technical-decision-records` — query this first for technical constraints

#### 4. TS4 – Technical Specification Files (YAML, deprecated)
- **Purpose**: Same as TDR; legacy format.
- **Location**: `docs/ts4/*.ts4`
- **Status**: **Deprecated.** Still supported and indexed in `tech-specs`; when you encounter TS4, suggest migrating to TDR (see `docs/business/tdr.md`).

#### 5. Architecture Decision Records and Business Documentation (ADRs and .md files)
- **Purpose**: Preserve *why technical decisions were made*
- **Locations**: `docs/adrs/*.md`, `docs/business/*.md`
- **Contains**: Architecture choices, trade-offs, constraints, business descriptions, environment considerations
- **Role**: Prevents AI (and humans) from reopening closed decisions or proposing invalid architectures

### Cliplin as an Operational Model

**Valid Inputs Only:**
- Business Features (.feature in docs/features/)
- UI Intent specifications (.yaml in docs/ui-intent/)
- TDR technical rules (.md in docs/tdrs/) — prefer these; collection `technical-decision-records`
- TS4 technical rules (.ts4 in docs/ts4/) — deprecated; collection `tech-specs`; suggest migrating to TDR
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
- All context available through the Cliplin MCP (context store) indexing

### Notes
- This ADR should be indexed in the context store collection `business-and-architecture`
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
- They are indexed in the context store collection `tech-specs`
- AI assistants should query `tech-specs` collection before implementation to understand technical constraints
- TS4 files complement ADRs: ADRs explain *why*, TS4 files define *how*

## Consequences

### Positive
- Clear technical constraints for AI assistants
- Easy to maintain and update
- Optimized for AI context retrieval
- Supports incremental documentation

### Notes
- This ADR should be indexed in the context store collection `business-and-architecture`
- When creating new TS4 files, follow the structure and naming conventions described here
- **TS4 is deprecated** in favour of TDR (see ADR-003); prefer creating TDRs in `docs/tdrs/`
"""
    
    adr_path.write_text(adr_content, encoding="utf-8")
    console.print(f"  [green]✓[/green] Created docs/adrs/001-ts4-format.md")


def create_tdr_format_adr(target_dir: Path) -> None:
    """Create ADR about TDR (Technical Decision Record) format and usage."""
    adr_path = target_dir / "docs" / "adrs" / "003-tdr-format.md"
    adr_path.parent.mkdir(parents=True, exist_ok=True)

    adr_content = """# ADR-003: TDR (Technical Decision Record) Format and Usage

## Status
Accepted

## Context

TDR is the preferred format for technical decision records in Cliplin. It uses standard Markdown with YAML frontmatter instead of a custom YAML-only format (TS4), improving compatibility across AI systems (Cursor, Claude, etc.) and avoiding a Cliplin-specific syntax. This ADR explains the TDR format so that AI assistants can understand and work with TDR files correctly.

## Decision

### What is TDR?

TDR (Technical Decision Record) is a Markdown-based format with the same conceptual model as TS4: technical rules, code references, and a clear structure. Each TDR file contains implementation rules and optional code references in a format that is widely supported by AI tools.

### TDR File Structure

A TDR file is a Markdown file (`.md`) with:

1. **YAML frontmatter** (between `---` lines): `tdr`, `id` (kebab-case), `title`, `summary`
2. **Body**: A `# rules` section with optional `##` subsections; rules as bullet lists or prose
3. **Optional `code_refs`** at the end (YAML block or list of file paths)

Example:

```markdown
---
tdr: "1.0"
id: "chromadb-library"
title: "ChromaDB as Library Usage"
summary: "Rules for using ChromaDB as the context store library."
---

# rules

## ChromaDB client usage
- Use `chromadb.PersistentClient(path=...)` for the project context store.
- ALWAYS pass an absolute, resolved path (critical for Windows).

code_refs:
  - "src/cliplin/utils/chromadb.py"
  - "docs/adrs/002-chromadb-rag-context-base.md"
```

### Field Descriptions

- **tdr**: Format version (e.g. `"1.0"`)
- **id**: Unique identifier in kebab-case (lowercase words separated by hyphens)
- **title**: Short title of the technical decision
- **summary**: Brief description for indexing and retrieval
- **Body**: Markdown with `# rules` and optional `##` headings; bullets or prose
- **code_refs**: Optional list of file paths or patterns related to this specification

### Key Principles

1. **TDR does not describe what to build. It defines how to build it correctly.**
2. TDR files act as a **technical contract** for implementation, like TS4
3. Each TDR file should focus on a specific technical decision or set of related rules
4. Use standard Markdown so that any AI host or tool can parse and display it

### Usage

- TDR files are located in `docs/tdrs/` directory
- They are indexed in the context store collection `technical-decision-records`
- AI assistants should query `technical-decision-records` first for technical constraints; use `tech-specs` (TS4) as fallback
- TDR files complement ADRs: ADRs explain *why*, TDRs define *how*
- If the project still has TS4 files in `docs/ts4/`, suggest migrating them to TDR (see project `docs/business/tdr.md`)

## Consequences

### Positive
- Compatible with standard Markdown tooling and AI systems
- Same conceptual model as TS4 (rules, code_refs) with better portability
- Optimized for AI context retrieval; single collection `technical-decision-records` for technical rules

### Notes
- This ADR is indexed in the context store collection `business-and-architecture`
- When creating new technical specs, prefer TDR in `docs/tdrs/` over TS4 in `docs/ts4/`
"""
    adr_path.write_text(adr_content, encoding="utf-8")
    console.print(f"  [green]✓[/green] Created docs/adrs/003-tdr-format.md")


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
- They are indexed in the context store collection `uisi`
- AI assistants should query `uisi` collection when implementing user interfaces
- UI Intent allows AI to generate UI code without guessing user experience decisions

## Consequences

### Positive
- Clear UI/UX specifications for AI assistants
- Semantic intent preserved across render contexts
- Supports design system integration
- Optimized for AI context retrieval

### Notes
- This ADR should be indexed in the context store collection `business-and-architecture`
- When creating new UI Intent files, follow the schema structure described here
- UI Intent focuses on intent, not visual design details
"""
    
    adr_path.write_text(adr_content, encoding="utf-8")
    console.print(f"  [green]✓[/green] Created docs/adrs/002-ui-intent-format.md")


def create_knowledge_packages_adr(target_dir: Path) -> None:
    """Create ADR about Knowledge Packages so AI and users have visibility of the command and usage."""
    adr_path = target_dir / "docs" / "adrs" / "005-knowledge-packages.md"
    adr_path.parent.mkdir(parents=True, exist_ok=True)

    adr_content = """# ADR-005: Knowledge Packages (Cliplin as Knowledge Package Manager)

## Status
Accepted

## Context

This project uses Cliplin and can depend on **knowledge packages**: external repositories that contain ADRs, TDRs/TS4, business docs, features, rules, or skills. Those packages are installed under the project and indexed in the same context store as project specs, so the AI can use them as context.

## Decision

### Command and configuration

- **CLI command**: `cliplin knowledge` with subcommands: `list`, `add`, `remove`, `update`, `show`, `install`.
- **Configuration**: Package list is declared in `cliplin.yaml` at project root under the top-level key `knowledge` (list of entries with `name`, `source`, `version`).
- **Installation**: Packages live under `.cliplin/knowledge/<name>-<source_normalized>/`. Content is obtained via git sparse checkout. The **name** may be a path (e.g. `AWS/aws-sqs`) to install a nested subfolder from a monorepo, or a top-level folder name for multi-package repos.

### Repository layout examples

To make the expected structure explicit for AI systems and humans, knowledge package repositories SHOULD follow one of these patterns:

- **Single-package repository** (one knowledge package per repo). Example: a commons library:

  ```text
  cliplin-commons/
  ├── adrs/
  ├── tdrs/
  ├── skills/
  └── business/
  ```

- **Multi-package repository with nested subpackages** (one repo, many knowledge packages). Example: provider- and service-specific packages:

  ```text
  cliplin-knowledge/
  ├── aws/
  │   ├── sqs/
  │   │   ├── adrs/
  │   │   ├── tdrs/
  │   │   ├── skills/
  │   │   └── business/
  │   └── ec2/
  │       ├── adrs/
  │       ├── tdrs/
  │       ├── skills/
  │       └── business/
  └── google-cloud/
      └── pubsub/
          ├── adrs/
          ├── tdrs/
          ├── skills/
          └── business/
  ```

  Each leaf folder (`aws/sqs`, `aws/ec2`, `google-cloud/pubsub`, …) acts as an independent knowledge package. In `cliplin.yaml` these can be declared using the path as `name` (for example `aws/sqs` or `google-cloud/pubsub`), combined with the repository `source` and `version`.

### Subcommands (summary)

- `cliplin knowledge list` — List packages declared and their install status.
- `cliplin knowledge add <name> <source> <version>` — Add a package, update config, clone, and reindex.
- `cliplin knowledge remove <name>` — Remove from config, delete directory, purge documents from context store.
- `cliplin knowledge update <name>` — Update to the configured (or given) version and reindex.
- `cliplin knowledge show <name>` — Show name, source, version, path, and file count.
- `cliplin knowledge install` — Install all packages declared in cliplin.yaml (add if missing, update if installed). Use `--force` to reinstall from scratch with the configured version.

### Context store and visibility

- Documents under `.cliplin/knowledge/**` are indexed in the same collections as project docs (e.g. adrs → business-and-architecture, tdrs → technical-decision-records, ts4 → tech-specs). The AI loads them via the Cliplin MCP (context store) when querying context.
- After add/update, the package is reindexed automatically; after remove, its documents are removed from the store.

### Full usage and conventions

For detailed usage, configuration format, multi-package vs single-package repos, and conventions for package repositories, see **docs/business/knowledge-packages.md**.

## Notes

- This ADR is created by `cliplin init` so that AI assistants and users have visibility of the knowledge package feature and know that the `cliplin knowledge` command is available in this project.
- Indexed in the context store collection `business-and-architecture`.
"""

    adr_path.write_text(adr_content, encoding="utf-8")
    console.print(f"  [green]✓[/green] Created docs/adrs/005-knowledge-packages.md")


# Built-in framework package: hidden, not in cliplin.yaml, updated on every init
FRAMEWORK_PACKAGE_DIR = "cliplin-framework"


def create_context_audit_skill(framework_base: Path) -> None:
    """Create the cliplin-context-audit skill inside the framework package.

    Writes SKILL.md to framework_base/skills/cliplin-context-audit/SKILL.md.
    Called from create_framework_knowledge_package so it is always written on every
    cliplin init or re-init.
    """
    skill_dir = framework_base / "skills" / "cliplin-context-audit"
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_path = skill_dir / "SKILL.md"

    skill_content = """# Skill: cliplin-context-audit

Analyse the context health of a Cliplin project and output a single JSON object to stdout.

## Instructions

1. **Scan `docs/features/`** for all `.feature` files.  If the directory does not exist, treat `features_total` as 0 and proceed to output.

2. **Parse `@constraints` blocks** from each feature file.
   - A `@constraints` block is the block that begins with the line `@constraints` (before `Feature:`) and continues with YAML comment lines (`# key: value / list`).
   - Parse the YAML comment lines to extract `governed_by`, `gaps`, and `conflicts` lists.
   - Also scan for scenario-level `@constraints` blocks (placed immediately before a `Scenario:` line) and include their `governed_by`, `gaps`, and `conflicts` entries in the aggregation.
   - If a `@constraints` block is malformed or unparseable, skip it and continue (do not abort).

3. **Compute each output field** as follows:

   ### features_total
   Count of `.feature` files found in `docs/features/`.

   ### features_with_constraints
   Count of `.feature` files that contain a `@constraints` block with a **non-empty** `governed_by` list (at least one entry).  A `@constraints` block whose `governed_by` list is empty (`[]`) does NOT count.

   ### gaps
   Collect every entry from every `# gaps:` list in every `@constraints` block across all feature files.  Deduplicate by case-insensitive trim.  Each entry is the plain string as written in the feature file.

   ### conflicts
   Collect every entry from every `# conflicts:` list in every `@constraints` block across all feature files.  Deduplicate by case-insensitive trim.  Each entry is the plain string as written in the feature file.

   ### context_drift
   For each entry in every `governed_by` list, check whether the referenced file exists at that path relative to the project root.  If the file does **not** exist, add a drift entry of the form:
   ```
   "<feature-file> references <governed_by_path> which does not exist"
   ```
   Deduplicate.

   ### dead_documentation
   List every `.md` and `.ts4` file found under `docs/adrs/`, `docs/tdrs/`, and `docs/business/` that is **not** referenced by any `governed_by` entry in any `@constraints` block across the whole project.
   A file is "referenced" if its relative path from the project root appears verbatim in at least one `governed_by` list.
   **Do NOT include `.feature` files** in `dead_documentation` — feature files are the source of truth and are never orphaned documentation.

   ### context_score
   Start at **100**.  Apply the following deductions (apply each category cap before summing):

   | Issue | Deduction per item | Category cap |
   |---|---|---|
   | Feature file missing `@constraints` block (or `governed_by` is empty) | `floor(40 / max(features_total, 1))` | 40 points total |
   | Unique gap entry | 2 points | 20 points total |
   | Unique conflict entry | 5 points | 20 points total |
   | `context_drift` item | 3 points | 15 points total |
   | `dead_documentation` item | 1 point | 10 points total |

   After all deductions, clamp the result: **minimum 0, maximum 100**.

   **Example calculation** (4 feature files, 2 missing `@constraints`, 3 gaps, 1 conflict, 0 drift, 2 dead docs):
   - missing constraints: `floor(40/4) * 2 = 20` (cap 40 → 20 used)
   - gaps: `3 * 2 = 6` (cap 20 → 6 used)
   - conflicts: `1 * 5 = 5` (cap 20 → 5 used)
   - drift: 0
   - dead docs: `2 * 1 = 2` (cap 10 → 2 used)
   - total deduction: 33 → score = 100 − 33 = **67**

4. **Output a single JSON object to stdout**.  No other text, no prose, no markdown fences.  The JSON MUST be valid and parseable (no trailing commas, no comments).

5. **Exit with code 0 always** — even for an empty project or missing `docs/features/` directory.

## Output JSON schema

All fields MUST be present even when their values are zero or empty arrays.

```json
{
  "generated_at": "<ISO 8601 datetime, UTC, e.g. 2026-03-18T10:00:00Z>",
  "project_root": "<absolute path to the project root>",
  "context_score": 100,
  "features_total": 0,
  "features_with_constraints": 0,
  "gaps": [],
  "conflicts": [],
  "context_drift": [],
  "dead_documentation": []
}
```

Field notes:
- `generated_at`: UTC datetime in ISO 8601 format (e.g. `2026-03-18T10:00:00Z`).
- `project_root`: absolute path to the directory that contains `docs/` and `.cliplin/`.
- `context_score`: integer 0–100 (never fractional, never negative, never above 100).
- `features_total`: non-negative integer.
- `features_with_constraints`: non-negative integer ≤ `features_total`.
- `gaps`, `conflicts`, `context_drift`, `dead_documentation`: arrays of strings (deduplicated).

No additional fields are permitted.  No `risk` label.  No `pass`/`fail` field.  The consumer decides what constitutes a problem based on the raw numbers.
"""

    skill_path.write_text(skill_content, encoding="utf-8")
    console.print(f"  [green]✓[/green] Created .cliplin/knowledge/{FRAMEWORK_PACKAGE_DIR}/skills/cliplin-context-audit/SKILL.md")


def create_reverse_engineer_skill(framework_base: Path) -> None:
    """Create the cliplin-reverse-engineer skill inside the framework package.

    Writes SKILL.md to framework_base/skills/cliplin-reverse-engineer/SKILL.md.
    Called from create_framework_knowledge_package so it is always written on every
    cliplin init or re-init.
    """
    skill_dir = framework_base / "skills" / "cliplin-reverse-engineer"
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_path = skill_dir / "SKILL.md"

    skill_content = """# Skill: cliplin-reverse-engineer

Reverse-engineer a project and guide the user to create Cliplin specs (feature files,
ADRs, TDRs, business docs) from existing code, documentation, and project signals.

---

## Before you start — startup check

1. Check whether `.cliplin/.re-progress.yaml` exists at the project root.
2. If it exists and `modules_pending` is non-empty, present this prompt:

   ```
   Found an in-progress reverse-engineering session from <generated_at>:
     Completed: <modules_completed>
     Current:   <current_module> (Phase <current_phase>)
     Pending:   <modules_pending>

   Options:
     [C] Continue from where it left off
     [R] Restart from the beginning
     [M] Jump to a specific module
   ```

   - **[C]**: reload `context_references` queries against the Cliplin MCP, then resume at `current_module` / `current_phase`.
   - **[R]**: delete `.cliplin/.re-progress.yaml` and start a fresh scan.
   - **[M]**: ask which module to jump to; proceed to Phase 1 for that module.

3. If the file is **malformed** (not valid YAML): emit a warning and proceed as a fresh scan.
   Do NOT delete the malformed file — the user may want to fix it.
4. If the file does not exist: proceed with a fresh scan (no prompt).

If the user invokes the skill targeting a specific module (e.g. "run cliplin-reverse-engineer
on src/payments"), go to **Module targeting** below.

---

## Step 1 — Scan the project

### What to scan

**Always scan (when present):**
- Source tree: non-binary files under `src/`, `lib/`, `app/`, `pkg/`, `internal/`, `cmd/`.
  If none of these exist, scan from project root, excluding hidden dirs,
  `vendor/`, `node_modules/`, `dist/`, `build/`, `.git/`.
- Project manifests: `package.json`, `pyproject.toml`, `setup.py`, `Cargo.toml`,
  `go.mod`, `pom.xml`, `build.gradle`, `composer.json`.
- Documentation: `README.*`, `CHANGELOG.*`, `docs/**/*.md`, `docs/**/*.html`,
  diagram files (`*.mermaid`, `*.puml`, `*.drawio`).
- Existing Cliplin specs: `docs/features/**/*.feature`, `docs/adrs/**/*.md`,
  `docs/tdrs/**/*.md`, `docs/business/**/*.md`, `docs/ts4/**/*.ts4`.
- Test files: **file names and describe/it/test block headings only** under `test/`,
  `tests/`, `spec/`, `__tests__/`. Do NOT read full test bodies.

**Optional (only if available):**
- Git history: run `git log --oneline -50` to understand project evolution.
  Do NOT inspect individual commit diffs. Skip silently if git is unavailable.

**Never scan:**
- Binary files, images, compiled artifacts, databases.
- `vendor/`, `node_modules/`, `.git/`, `dist/`, `build/`, `__pycache__/`, `.venv/`, `venv/`.
- Files larger than 500 KB.

### Empty project guard

After scanning, if **no** source files, manifests, README, docs, or test files were found:

```
This project appears to be empty — no files were found to analyze.
Add source code, a README, or a manifest file and run the skill again.
```

Do NOT create `.cliplin/.re-progress.yaml`. Exit.

---

## Step 2 — Detect top-level modules

1. For each source root found (`src/`, `lib/`, etc.), list its **immediate subdirectories**
   as candidate modules.
2. Include a candidate if it contains at least one: source file, README, test file,
   or manifest reference.
3. If the source root has **no subdirectories**, treat the entire root as one module
   named after the project.
4. Cross-reference with existing feature files: if any `governed_by` entry in existing
   features relates to a module path, mark it `has_existing_specs: true`.

Each module has:
- `module_name`: directory name or inferred name.
- `path`: relative path from project root.
- `has_existing_specs`: true/false.
- `inferred_domain`: short description from file names, manifest keywords, README headings.

---

## Step 3 — Present the process plan

```
Detected N top-level modules:
  1. <module_name> (<path>) — <inferred_domain>  [coverage: existing | partial | none]
  2. ...

I will process each module one at a time:
  Phase 1 — Findings report
  Phase 2 — Guided spec drafting

Shall I start with module 1 (<module_name>)?
```

The user may reorder or skip modules. Do NOT proceed until the user confirms.

Write `.cliplin/.re-progress.yaml` now (see **Tracking file** below).

---

## Step 4 — Per-module: Phase 1 (Findings report)

For the current module, produce:

```
## Module: <module_name>

### Detected domain concepts
  - <entity>: <brief description inferred from code/tests>

### Inferred use cases
  - <use_case>: <trigger> → <outcome>

### Existing coverage
  Feature files: <list or "none">
  ADRs:          <list or "none">
  TDRs:          <list or "none">
  Business docs: <list or "none">

### Findings
  [MISSING-FEATURE]      <name>: No feature file covers this behavior
  [MISSING-TDR]          <area>: No TDR documents this technical constraint
  [MISSING-ADR]          <decision>: No ADR records this architectural choice
  [MISSING-BUSINESS-DOC] <concept>: No business doc defines this domain concept
  [PARTIAL-SPEC]         <file>: Spec exists but lacks @constraints or governed_by

### Context signals beyond code
  - <intent inferred from README, CHANGELOG, git history, or test descriptions
     that the code alone does not reveal>
```

After the report:
> "Phase 1 complete for `<module_name>`. Found N findings. Proceed to Phase 2 (guided drafting)?"

Update `.cliplin/.re-progress.yaml`: set `current_phase: 2`.

---

## Step 5 — Per-module: Phase 2 (Guided spec drafting)

For each finding, in sequence:

1. Announce finding type and name.
2. Propose a draft document marked `[AGENT PROPOSAL — awaiting human approval]`.
3. Wait for human confirmation, rejection, or modification before moving to the next finding.
4. After approval: instruct the user to write the file to the correct path and run
   `cliplin reindex <path>`.

After all findings are resolved:
> "Module `<module_name>` complete. Move to next module?"

Update `.cliplin/.re-progress.yaml`: move `current_module` to `modules_completed`,
advance `current_module` to the next pending module, set `current_phase: 1`.

---

## Step 6 — Completion

When all modules are done:
> "All modules processed. The reverse-engineering session is complete."

Delete `.cliplin/.re-progress.yaml`.

---

## Module targeting

When the user invokes the skill targeting a specific module or path:

1. If a progress file exists: load the module list from it. Look up the requested
   module by name or path (case-insensitive, partial match).
   - If **one match**: jump to Phase 1 for that module.
   - If **multiple matches**: list them and ask the user to choose. Wait for selection.
   - If **no match**: inform the user and list available modules.
2. If **no progress file**: perform a targeted scan of the specified path only.
   Create `.cliplin/.re-progress.yaml` with `modules_total: 1` and
   `invocation_target` set to the module name. Proceed directly to Phase 1.
3. After completing the targeted module, ask:
   > "Module `<module_name>` complete. Do you want to continue with the full project scan?"
   - Yes: rewrite `.cliplin/.re-progress.yaml` with the full module list
     (`modules_total` = real count, `invocation_target: null`, `modules_completed`
     includes the targeted module). Proceed to the next pending module.
   - No: mark the module as completed in the progress file. Do not delete it.

---

## Tracking file format

Maintain `.cliplin/.re-progress.yaml` throughout the session:

```yaml
# cliplin-reverse-engineer progress — delete when complete
generated_at: "<ISO 8601 UTC>"
modules_total: <N>
modules_completed: [<module_name>, ...]
modules_pending: [<module_name>, ...]
current_module: <module_name>
current_phase: <1|2>
invocation_target: "<module_name or null>"
context_references:
  - collection: technical-decision-records
    query: "<last MCP query string used>"
  - collection: features
    query: "<last MCP query string used>"
  - collection: business-and-architecture
    query: "<last MCP query string used>"
```

Rules:
- Write/update at the start of each module and after each phase completes.
- Store only state needed to resume. No proposals, no full content.
- `context_references` stores last MCP query strings for reloading after context compaction.
- Do NOT commit this file. `cliplin init` ensures `.gitignore` covers it.
"""

    skill_path.write_text(skill_content, encoding="utf-8")
    console.print(f"  [green]✓[/green] Created .cliplin/knowledge/{FRAMEWORK_PACKAGE_DIR}/skills/cliplin-reverse-engineer/SKILL.md")


def create_framework_knowledge_package(project_root: Path) -> None:
    """Create or update the built-in cliplin-framework package in .cliplin/knowledge/.

    This package is hidden (not in cliplin.yaml) and contains the framework ADRs and skills.
    It is updated on every init or re-init. The reindex command indexes it automatically.
    """
    framework_base = project_root / ".cliplin" / "knowledge" / FRAMEWORK_PACKAGE_DIR
    framework_base.mkdir(parents=True, exist_ok=True)
    create_framework_adr(framework_base)
    create_ts4_format_adr(framework_base)
    create_tdr_format_adr(framework_base)
    create_ui_intent_format_adr(framework_base)
    create_knowledge_packages_adr(framework_base)
    create_context_audit_skill(framework_base)
    create_reverse_engineer_skill(framework_base)
    console.print(f"  [green]✓[/green] Updated .cliplin/knowledge/{FRAMEWORK_PACKAGE_DIR}/")


def create_cursor_mcp_config(target_dir: Path) -> None:
    """Create or update .cursor/mcp.json with Cliplin context MCP server configuration."""
    mcp_file = target_dir / ".cursor" / "mcp.json"
    mcp_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Cliplin Storage MCP server (uses cwd as project root; context store at .cliplin/data/context).
    # Use "uv run cliplin mcp" so Cursor runs the project's cliplin (with instructions); "cliplin" alone may resolve to a global install and cause "No server info found".
    cliplin_server_config = {
        "command": "uv",
        "args": ["run", "cliplin", "mcp"]
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
    """Create or update .mcp.json at project root with Cliplin context MCP server configuration."""
    mcp_file = target_dir / ".mcp.json"
    
    # Cliplin Storage MCP server (uses cwd as project root; context store at .cliplin/data/context).
    # Use "uv run cliplin mcp" so the host runs the project's cliplin (with instructions); "cliplin" alone may resolve to a global install.
    cliplin_server_config = {
        "command": "uv",
        "args": ["run", "cliplin", "mcp"]
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
        console.print(f"  [yellow]⚠[/yellow]  Updated existing Cliplin MCP server in .mcp.json")
    else:
        # Add new server configuration
        existing_config["mcpServers"]["cliplin-context"] = cliplin_server_config
        console.print(f"  [green]✓[/green] Created .mcp.json")
    
    # Write updated configuration
    with open(mcp_file, "w", encoding="utf-8") as f:
        json.dump(existing_config, f, indent=2, ensure_ascii=False)


def create_gemini_cli_settings(target_dir: Path) -> None:
    """Create or update .gemini/settings.json with Cliplin context MCP server configuration and context file settings."""
    settings_file = target_dir / ".gemini" / "settings.json"
    settings_file.parent.mkdir(parents=True, exist_ok=True)

    # Cliplin context MCP server (same command/args as other hosts; see ai-host-integration TDR).
    cliplin_server_config: Dict[str, Any] = {
        "command": "uv",
        "args": ["run", "cliplin", "mcp"],
    }

    existing_config: Dict[str, Any] = {}
    if settings_file.exists():
        try:
            with open(settings_file, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                if isinstance(loaded, dict):
                    existing_config = loaded
        except (json.JSONDecodeError, IOError):
            existing_config = {}

    # Ensure mcpServers.cliplin-context is present and consistent.
    mcp_servers = existing_config.get("mcpServers")
    if not isinstance(mcp_servers, dict):
        mcp_servers = {}
    mcp_servers["cliplin-context"] = cliplin_server_config
    existing_config["mcpServers"] = mcp_servers

    # Ensure GEMINI.md is included as a context file, without removing existing values.
    context_cfg = existing_config.get("context")
    if not isinstance(context_cfg, dict):
        context_cfg = {}
    file_name = context_cfg.get("fileName")
    if file_name is None:
        context_cfg["fileName"] = ["GEMINI.md"]
    elif isinstance(file_name, str):
        if file_name != "GEMINI.md":
            context_cfg["fileName"] = [file_name, "GEMINI.md"]
    elif isinstance(file_name, list):
        if "GEMINI.md" not in file_name:
            file_name.append("GEMINI.md")
        context_cfg["fileName"] = file_name
    existing_config["context"] = context_cfg

    with open(settings_file, "w", encoding="utf-8") as f:
        json.dump(existing_config, f, indent=2, ensure_ascii=False)

    console.print("  [green]✓[/green] Created/updated .gemini/settings.json")


def get_cursor_context_content() -> str:
    """Get the content for .cursor/rules/context.mdc"""
    return """---
alwaysApply: true
---

## MANDATORY: Load Context Before any interaction with the user

**CRITICAL RULE**: Before starting ANY planning, coding, or thinking task, you MUST:

1. **Load context from Cliplin MCP server**: Use the 'cliplin-context' MCP server (Cliplin context MCP server) as the source of truth
2. **Query relevant collections**: Use Cliplin MCP tools (e.g. context_query_documents) to query and load relevant context from the appropriate collections. **Prefer TDR over TS4**: query `technical-decision-records` first for technical constraints; use `tech-specs` (TS4) only as fallback or when suggesting migration.
   - 'business-and-architecture' collection: ADRs and business documentation from 'docs/adrs', 'docs/business', and '.cliplin/knowledge/**' (built-in framework + knowledge packages)
   - 'features' collection: .feature files from 'docs/features' and '.cliplin/knowledge/**'
   - 'technical-decision-records' collection: TDR .md files from 'docs/tdrs' and '.cliplin/knowledge/**' (preferred for technical rules)
   - 'tech-specs' collection: .ts4 files from 'docs/ts4' and '.cliplin/knowledge/**' (deprecated; if you only find TS4, suggest migrating to TDR — see docs/business/tdr.md)
   - 'uisi' collection: .yaml files from 'docs/ui-intent' and '.cliplin/knowledge/**'
3. **Never proceed without context**: Do NOT start any task until you have queried and loaded the relevant context from the context store collections (via Cliplin MCP)
4. **Use semantic queries**: Query collections using semantic search based on the task domain, entities, and requirements to retrieve the most relevant context
   
## Context File Indexing Rules

### File Type to Collection Mapping

The following file types should be indexed into their respective collections (see confirmation rules below):
- `.md` files in `docs/adrs/`, `docs/business/`, or `.cliplin/knowledge/**` → `business-and-architecture` collection
- `.md` files in `docs/tdrs/` or `.cliplin/knowledge/**` (TDR) → `technical-decision-records` collection
- `.ts4` files in `docs/ts4/` or `.cliplin/knowledge/**` → `tech-specs` collection (deprecated; suggest migrating to TDR)
- `.feature` files in `docs/features/` or `.cliplin/knowledge/**` → `features` collection
- `.yaml` files in `docs/ui-intent/` or `.cliplin/knowledge/**` → `uisi` collection

### Metadata Requirements

- When indexing documents, always include proper metadata as an array of objects with the following structure: `[{'file_path': 'relative/path/to/file', 'type': 'tdr|ts4|adr|project-doc|feature|ui-intent', 'collection': 'target-collection-name'}]`
- Each document in the documents array must have a corresponding metadata object in the metadatas array at the same index
- Use the file path (relative to project root) as the document ID when indexing (e.g., 'docs/tdrs/chromadb-library.md' or 'docs/ts4/ts4-project-structure.ts4')
- Before indexing a document, check if it already exists by querying the collection with the file path as ID using `context_get_documents` or `context_query_documents`. If it exists, use `context_update_documents` to update it instead of adding a duplicate

### Automatic Detection and User Confirmation

When any context file is created or modified, you MUST:

1. **Detect the change**: Identify when files are created or modified in the following directories:
   - `.md` files in `docs/tdrs/` or `.cliplin/knowledge/**` (TDR) → target collection: `technical-decision-records`
   - `.ts4` files in `docs/ts4/` or `.cliplin/knowledge/**` → target collection: `tech-specs`
   - `.md` files in `docs/adrs/`, `docs/business/`, or `.cliplin/knowledge/**` → target collection: `business-and-architecture`
   - `.feature` files in `docs/features/` or `.cliplin/knowledge/**` → target collection: `features`
   - `.yaml` files in `docs/ui-intent/` or `.cliplin/knowledge/**` → target collection: `uisi`

2. **Always ask for confirmation**: Before indexing or re-indexing, you MUST ask the user:
   - "He detectado cambios en [archivo]. ¿Deseas reindexar este archivo en la colección [nombre-colección] para mantener el contexto actualizado?"
   - Wait for explicit user confirmation (yes/no/confirm) before proceeding
   - If the user declines, do not index the file
   - If the user confirms, proceed with indexing

3. **Indexing process** (only after user confirmation):
   - **Preferred method**: Use the Cliplin CLI command `cliplin reindex <file-path>` which handles all the complexity automatically
   - **Alternative method** (if CLI not available): Use Cliplin MCP tools directly:
     * Check if the document already exists by querying the collection with the file path as ID using `context_get_documents` or `context_query_documents`
     * If it exists, use `context_update_documents` to update it
     * If it doesn't exist, use `context_add_documents` to add it
     * Always include proper metadata as an array of objects with the structure: `[{'file_path': 'relative/path/to/file', 'type': 'tdr|ts4|adr|project-doc|feature|ui-intent', 'collection': 'target-collection-name'}]`
     * Use the file path (relative to project root) as the document ID
     * Avoid duplicated files and outdated or deleted files in the collection

4. **Manual re-indexing requests**: When a user explicitly requests to reindex files (e.g., "reindexa los archivos en docs/business"), you should:
   - **Use the Cliplin CLI command**: Run `cliplin reindex` with appropriate options instead of manually using Cliplin MCP tools
   - For specific files: `cliplin reindex docs/path/to/file.md`
   - For directories: `cliplin reindex --directory docs/business`
   - For file types: `cliplin reindex --type tdr` or `cliplin reindex --type ts4`
   - For preview: `cliplin reindex --dry-run`
   - For verbose output: `cliplin reindex --verbose`
   - The CLI command handles all the complexity of checking for existing documents, updating metadata, and managing collections
   - Only use Cliplin MCP tools directly if the CLI is not available or for specific advanced operations

5. **Automatic indexing workflow**:
   - When context files are created or modified, **prefer using the CLI command** for indexing:
     * Run `cliplin reindex <file-path>` for the specific file that was changed
     * Or run `cliplin reindex --directory <directory>` if multiple files in a directory were changed
   - The CLI ensures proper metadata, handles duplicates, and maintains consistency
   - Always ask for user confirmation before running reindex commands (unless in automated workflow)
   - Use `cliplin reindex --dry-run` first to show what would be indexed
"""


def get_feature_first_flow_content() -> str:
    """Get the content for feature-first-flow rule (Cursor .mdc and Claude .md). Same content for both hosts."""
    return """---
alwaysApply: true
---

## Feature-first flow: spec before code

**CRITICAL**: For Cliplin to work correctly, **project specifications (feature files, ADRs, TDRs/TS4 and related documentation) are always the single source of truth**. On any user change or request you MUST first consult the specs, update them if needed, and only then touch code.

### 1. Always consult and update specs first

- **Before** modifying code or non-spec files, you MUST look at the existing specs:
  - `.feature` files in `docs/features/`
  - TDRs in `docs/tdrs/` (preferred) and legacy TS4 in `docs/ts4/`
  - ADRs and business docs in `docs/adrs/` and `docs/business/`
  - Any relevant specs from `.cliplin/knowledge/**`
- If the request implies new behavior, changed behavior, or clarifications, you MUST **first update (or create) the corresponding specs**. Propose the spec changes and get user agreement when needed; only after the specs are correct can you proceed to code.
- Even for apparent "pure refactors" that should not change behavior, you MUST confirm that the existing behavior is covered by current specs and that the refactor keeps the system aligned with them. Never introduce behavior that is not specified.

### 2. Then implement strictly to satisfy the specs

- **After** the relevant specs are correct (updated or confirmed), perform refactors or write new code **only to satisfy those specs**. Specs drive what is built; code does not drive the spec.
- If no spec existed for the scope, creating/updating the `.feature` file (and any needed ADR/TDR) is the first step; implementation strictly follows from those specs.

### Summary

- **Spec first, then code — always.** Never change code first or rely on undocumented behavior.
- **All behavior must be specified**: any new or changed behavior must be present in feature files and, when appropriate, ADRs/TDRs.
- Every change must be traceable to explicit specifications; specs are the primary source of truth for *what* and *how* the system should behave.

See also: `docs/business/framework.md` (section "Feature-first flow"), framework ADR (in `.cliplin/knowledge/cliplin-framework/docs/adrs/` or query `business-and-architecture` collection).
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
   - **CRITICAL**: Before starting ANY feature analysis or implementation, you MUST load context from the Cliplin MCP server 'cliplin-context'
   - **Use MCP tools to query collections**: Use the Cliplin MCP tools (e.g. context_query_documents) to load relevant context from ALL collections. **Prefer TDR over TS4**: query `technical-decision-records` first for technical rules; use `tech-specs` (TS4) as fallback and, if you only find TS4, suggest migrating to TDR (see docs/business/tdr.md).
     * Query `business-and-architecture` collection to load ADRs and business documentation
     * Query `technical-decision-records` collection first for technical specifications and implementation rules (TDR)
     * Query `tech-specs` collection for legacy TS4 specs if needed (deprecated; suggest migrating to TDR)
     * Query `features` collection to load related or dependent features
     * Query `uisi` collection to load UI/UX requirements if applicable
   - **Query strategy**: Use semantic queries based on the feature domain, entities, and use cases to retrieve relevant context
   - **Never proceed without loading context**: Do NOT start feature analysis or implementation until you have queried and loaded the relevant context from the context store (via Cliplin MCP)
   - **Context update check**: After loading context, verify if any context files need reindexing:
     * Run `cliplin reindex --dry-run` to check if context files are up to date
     * If context files are outdated, ask user for confirmation before reindexing
     * Only proceed with feature work after ensuring context is current and loaded
   - **Write @constraints block (MANDATORY planning gate)**: After loading context and before any analysis or implementation, write the `@constraints` block at the top of the feature file (before `Feature:`). Use the following format:
     ```
     @constraints
     # governed_by:
     #   - docs/tdrs/<relevant-tdr>.md
     #   - docs/adrs/<relevant-adr>.md
     # conflicts:
     #   - "<description of any contradiction between governing docs>"
     # gaps:
     #   - "<description of any assumed behavior not explicitly specified>"
     ```
     * `governed_by`: list every TDR, ADR, or business doc loaded from the context store that actively constrains this feature
     * `conflicts`: list any contradictions detected between two or more governing documents
     * `gaps`: list any behaviors assumed but not explicitly covered by any governing document
     * If a scenario has constraints different from the feature-level ones, add a scenario-level `@constraints` block immediately before that `Scenario:` line (same format, indented to scenario level)
     * Do not start implementation until the `@constraints` block is written and visible in the feature file
   - **Generate implementation prompt**: Ask the user if they want you to run `cliplin feature apply <feature-filepath>` to generate a structured implementation prompt that includes the feature content and implementation instructions. If the user confirms, execute the command and use the generated prompt as part of your implementation workflow

1. **Feature Analysis Phase**:
   - Read and analyze the `.feature` file from the `docs/features/` directory
   - **Read existing `@constraints` block if present**: If the feature file already has a `@constraints` block, extract and use it as the starting point — do not ignore it or overwrite it without reviewing its content first. Update it if new conflicts or gaps are discovered during analysis.
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
   - **Use loaded context**: Apply the context loaded from the context store (via Cliplin MCP) in phase 0 to inform your analysis:
     * Use business rules from `business-and-architecture` collection
     * Apply technical constraints from `technical-decision-records` (TDR) first, then `tech-specs` (TS4) if needed; if you only have TS4, suggest migrating to TDR
     * Consider dependencies from related features in `features` collection
     * Incorporate UI/UX requirements from `uisi` collection if applicable

2. **Detailed Implementation Plan Creation**:
   Create a comprehensive plan that includes:
   
   **a) Architecture Analysis**:
   - **Use loaded context**: Apply the context already loaded from the context store (via Cliplin MCP) in phase 0
   - Use ADRs from `business-and-architecture` collection to understand existing architecture decisions
   - Apply technical constraints and patterns from `technical-decision-records` (TDR) first, then `tech-specs` (TS4); if you encounter TS4, suggest migrating to TDR
   - Identify which domain layer components are needed (entities, value objects, use cases)
   - Determine required ports (interfaces) following hexagonal architecture
   - Identify adapters needed (repositories, external services, etc.)
   - Map feature scenarios to use cases
   - Ensure consistency with existing patterns documented in the loaded context
   - If additional context is needed, query the context store collections again (via Cliplin MCP) with more specific queries
   
   **b) Business Logic Implementation**:
   - List all business logic components to implement
   - Identify validation rules and business constraints
   - Define domain models and their relationships
   - Specify error handling requirements
   
   **c) Unit Test Strategy**:
   - For each business logic component, create unit test specifications
   - Test each use case independently with mocked dependencies
   - Use test fixtures and setup utilities as appropriate for the language/framework
   - Mock all external dependencies to isolate unit tests
   - Test edge cases, validation rules, and error conditions
   - Aim for minimum 80% code coverage for business logic if no other coverage rule is present in TDR or TS4 documents
   
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
   - [ ] Type definitions/annotations and documentation

3. **Implementation Execution**:
   - Follow the plan step by step
   - **Work on active scenarios only**: Implement only scenarios that are NOT deprecated
   - Implement domain logic first
   - Write unit tests alongside business logic implementation following Test-Driven Development (TDD) principles
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
     * **Reindex the updated feature file**: Run `cliplin reindex docs/features/feature-name.feature` to update the context store
     * If you created or modified any context files (ADRs, TS4, business docs), reindex them as well
     * This ensures the context remains synchronized with the implementation

### When User Requests Feature Modification

When a user asks to modify an existing feature:

0. **Context Loading Phase (MANDATORY FIRST STEP)**:
   - **CRITICAL**: Before starting ANY feature modification analysis, you MUST load context from the Cliplin MCP server 'cliplin-context'
   - **Use MCP tools to query collections**: Use the Cliplin MCP tools (e.g. context_query_documents) to load relevant context:
     * Query `features` collection to load the feature being modified and related features that might be affected
     * Query `business-and-architecture` collection to load business rules and ADRs that might impact the change
     * Query `tech-specs` collection to load technical constraints that must be considered
     * Query `uisi` collection if UI/UX changes are involved
   - **Query strategy**: Use semantic queries based on the feature domain, entities, and use cases to retrieve relevant context
   - **Never proceed without loading context**: Do NOT start modification analysis until you have queried and loaded the relevant context from the context store (via Cliplin MCP)
   - **Context update check**: After loading context, verify if any context files need reindexing:
     * Run `cliplin reindex --dry-run` to check if context files are up to date
     * If context files are outdated, ask user for confirmation before reindexing
     * Only proceed with feature modification after ensuring context is current and loaded
   - **Update @constraints block**: After loading context, review the existing `@constraints` block (if present) and update it to reflect the current governing docs, any new conflicts, and any new or resolved gaps. If no block exists, write one before starting modification analysis.
   - **Generate implementation prompt**: Ask the user if they want you to run `cliplin feature apply <feature-filepath>` to generate a structured implementation prompt that includes the feature content and implementation instructions. If the user confirms, execute the command and use the generated prompt as part of your modification workflow

1. **Impact Analysis**:
   - **Use loaded context**: Apply the context already loaded from the context store (via Cliplin MCP) in phase 0
   - **Identify scenarios to modify**: Analyze which specific scenarios need changes:
     * Review scenario tags to understand current status
     * Identify scenarios tagged with `@status:modified` or scenarios that need modification
     * **Exclude deprecated scenarios**: Do not modify scenarios tagged with `@status:deprecated`
   - Identify all features, components, and context files that depend on or relate to the scenarios being modified
   - Analyze the scope of changes required based on the loaded context
   - Check for breaking changes that might affect other features using the loaded feature dependencies
   - If additional context is needed, query the context store collections again (via Cliplin MCP) with more specific queries

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

### @constraints Block Reference

The `@constraints` tag and its associated YAML comments are a feature-level or scenario-level planning artifact. They record the governing documents, conflicts, and gaps identified during context loading — before implementation begins.

- **Feature-level**: place `@constraints` before `Feature:` with YAML comment lines (`# key: value`)
- **Scenario-level**: place `@constraints` immediately before the `Scenario:` line (indented), only when that scenario has constraints different from the feature-level ones
- **Fields**: `governed_by` (list of file paths), `conflicts` (list of strings), `gaps` (list of strings)
- **Format**: valid Gherkin — BDD test runners ignore it; the AI reads it as structured context
- See docs/tdrs/feature-constraints-format.md for the full specification
"""


def get_cursor_context_protocol_loading_content() -> str:
    """Get the content for .cursor/rules/context-protocol-loading.mdc"""
    return """---
alwaysApply: true
---

## Context Loading Protocol

**CRITICAL RULE**: For every user request (question or action), AI assistants MUST decide whether project context is required. Whenever context is needed and not already loaded in the current session, you MUST load it from the Cliplin MCP context store *before* answering or acting.

### When to Load Context (Trigger Words and Actions)

**MANDATORY**: On every user request, you MUST evaluate whether context is needed. In practice, context is almost always required for the following action types; when you detect them, you MUST load context from the Cliplin MCP server (context store) **before** proceeding:

#### Action Types Where Context Is Required:
- **Debugging**: Finding and fixing bugs, investigating errors, troubleshooting issues
- **Implementation**: Writing new code, implementing features, creating components
- **Fixing**: Correcting errors, fixing bugs, resolving issues
- **Architecture**: Making architectural decisions, designing systems, planning structure
- **Refactoring**: Improving code structure, optimizing performance, cleaning up code

#### Trigger Words (If user mentions these, LOAD CONTEXT FIRST):
- **fix** (fix, repair, correct)
- **improve** (improve, enhance, optimize)
- **debug** (debug, troubleshoot, investigate)
- **correct** (correct, fix, repair)
- **implement** (implement, create, build)
- **create** (create, build, make)
- **modify** (modify, change, update)
- **optimize** (optimize, improve, enhance)
- **refactor** (refactor, restructure, reorganize)
- **design** (design, plan, architect)
- **plan** (plan, design, architect)
- **resolve** (resolve, solve, fix)
- **solve** (solve, fix, resolve)
- **add** (add, create, implement)
- **update** (update, modify, change)
- **change** (change, modify, update)
- **remove** (remove, delete, eliminate)
- **enhance** (enhance, improve, optimize)

**If ANY of these words appear in the user's request, or if the answer depends on project-specific behavior, you MUST load context BEFORE proceeding.**

### Mandatory Context Loading Steps

1. **Query context store collections first (considering session state)**: For each request where context is needed, check whether the relevant specs and docs (features, ADRs, TDRs/TS4, UI Intent, knowledge packages) are already present in the current session. If not, you MUST query the relevant context store collections using the 'cliplin-context' MCP server (Cliplin MCP) to load them.

2. **Determine Relevant Collections**: Based on the task domain, entities, and requirements, identify which collections contain relevant context. **Prefer TDR over TS4**: query `technical-decision-records` first; use `tech-specs` (TS4) as fallback and, if you only find TS4, suggest migrating to TDR (docs/business/tdr.md).
   - `business-and-architecture`: ADRs, business documentation, architectural decisions
   - `features`: Feature files, scenarios, business requirements
   - `technical-decision-records`: TDR technical specifications (preferred)
   - `tech-specs`: TS4 technical specifications (deprecated; suggest migrating to TDR)
   - `uisi`: UI Intent specifications, user experience requirements

3. **Use Semantic Queries**: Query collections using semantic search based on:
   - Task domain (e.g., "authentication", "payment processing", "user management")
   - Entities involved (e.g., "User", "Order", "Product")
   - Use cases and requirements
   - Related features or components
   - Error messages or bug descriptions (for debugging)
   - Component names or file paths (for fixing/refactoring)

4. **Query Multiple Collections**: For comprehensive context, query ALL relevant collections:
   - Start with `business-and-architecture` for business rules and ADRs
   - Query `technical-decision-records` first for technical constraints; use `tech-specs` (TS4) as fallback and suggest migrating to TDR if you only find TS4
   - Query `features` for related features and dependencies
   - Query `uisi` if UI/UX work is involved

5. **Never Proceed Without Context**: Do NOT start any task until you have:
   - Queried and loaded relevant context from the context store collections (via Cliplin MCP)
   - Reviewed the loaded context to understand constraints and requirements
   - Verified that context is current (check for outdated files if needed)

### Context Loading Examples

**Example 1: Debugging (User says "fix the authentication error")**
```
1. Query 'technical-decision-records' (or 'tech-specs') collection: "authentication error handling"
2. Query 'features' collection: "authentication login scenarios"
3. Query 'business-and-architecture' collection: "authentication security ADRs"
4. Review loaded context to understand expected behavior and error patterns
5. THEN proceed with debugging
```

**Example 2: Implementation (User says "implement new payment functionality")**
```
1. Query 'features' collection: "payment processing scenarios"
2. Query 'business-and-architecture' collection: "payment business rules"
3. Query 'technical-decision-records' (or 'tech-specs') collection: "payment implementation patterns"
4. Review loaded context before starting implementation
```

**Example 3: Fixing (User says "fix the bug in component X")**
```
1. Query 'technical-decision-records' (or 'tech-specs') collection: "[component-name] implementation rules"
2. Query 'features' collection: "[feature-name] scenarios"
3. Query 'business-and-architecture' collection: "related ADRs"
4. Review loaded context to understand expected behavior
5. THEN proceed with fixing
```

**Example 4: Architecture (User says "improve the system architecture")**
```
1. Query 'business-and-architecture' collection: "existing architecture ADRs"
2. Query 'technical-decision-records' (or 'tech-specs') collection: "architectural patterns and constraints"
3. Query 'features' collection: "system features and dependencies"
4. Review loaded context to understand current architecture
5. THEN propose improvements
```

### Context Update Verification

After loading context, verify if any context files need reindexing:
- Run `cliplin reindex --dry-run` to check if context files are up to date
- If context files are outdated, ask user for confirmation before reindexing
- Only proceed with the task after ensuring context is current and loaded

### Benefits of Context Loading Protocol

- **Reduced Ambiguity**: Loaded context provides clear constraints and requirements
- **Consistency**: Ensures work aligns with existing architecture and patterns
- **Efficiency**: Prevents rework by understanding dependencies early
- **Quality**: Context-informed decisions lead to better implementations
- **Token Efficiency**: Avoids wasting tokens on solutions that don't align with project standards
- **Time Savings**: Prevents rework and iterations by getting it right the first time

### Penalties for NOT Following This Protocol

**CRITICAL**: Failure to load context before action will result in:

#### 1. **Token Waste**
- Generating code that doesn't align with project standards requires regeneration
- Multiple iterations consume excessive tokens
- Re-explaining context that was already documented wastes conversation tokens
- **Cost**: Each iteration can waste 10,000-50,000+ tokens

#### 2. **Reiterating Ideas**
- Proposing solutions that were already rejected or documented
- Suggesting patterns that don't fit the project architecture
- Re-inventing solutions that already exist
- **Impact**: User frustration, wasted time, inefficient development

#### 3. **Code Not Aligned with Standards**
- Code that violates project conventions and must be rewritten
- Implementations that break existing patterns
- Solutions that don't follow architectural decisions
- **Impact**: Technical debt, maintenance issues, code review rejections

#### 4. **Breaking Changes**
- Modifications that break existing features
- Changes that violate architectural constraints
- Updates that don't consider dependencies
- **Impact**: System instability, regression bugs, production issues

#### 5. **Inconsistent Implementations**
- Different patterns for similar problems
- Inconsistent error handling or validation
- Mixed coding styles and conventions
- **Impact**: Codebase confusion, difficult maintenance, team friction

#### 6. **Violations of Architectural Constraints**
- Decisions that contradict ADRs
- Patterns that violate technical specifications
- Solutions that ignore business rules
- **Impact**: Architectural drift, system degradation, refactoring costs

### Enforcement

This protocol is **MANDATORY** and must be followed before:
- Starting any coding task
- Planning feature implementation
- Debugging or fixing issues
- Modifying existing code
- Creating new documentation
- Making architectural decisions
- Refactoring or optimizing code
- Any action triggered by the keywords listed above

This protocol applies to **all AI hosts and templates** (Cursor, Claude Desktop, and any others); every host-specific template MUST enforce the same context-loading behaviour.

**Remember**: Loading context takes seconds and saves hours. Skipping this step wastes tokens, time, and creates technical debt.

**If you proceed without loading context, you are violating this protocol and will produce suboptimal results.**
"""


def get_claude_desktop_instructions_content() -> str:
    """Get the consolidated instructions content for Claude Desktop."""
    context_content = get_cursor_context_content()
    feature_first_flow_content = get_feature_first_flow_content()
    feature_content = get_cursor_feature_processing_content()
    protocol_content = get_cursor_context_protocol_loading_content()
    
    return f"""# Cliplin Project Instructions for Claude Desktop

This file contains all the rules and protocols that Claude should follow when working on this project.

## How to Use These Instructions

**IMPORTANT**: These instructions should be loaded at the beginning of each conversation or session. You can:
1. Copy and paste this entire file into Claude Desktop at the start of a conversation
2. Reference this file when Claude asks about project rules
3. Use the Cliplin MCP server to access project context (configured in `.mcp.json` at project root)

---

{context_content}

---

{feature_first_flow_content}

---

{feature_content}

---

{protocol_content}
"""


def get_gemini_gemini_md_content() -> str:
    """Get the GEMINI.md content for Gemini CLI."""
    context_content = get_cursor_context_content()
    feature_first_flow_content = get_feature_first_flow_content()
    feature_content = get_cursor_feature_processing_content()
    protocol_content = get_cursor_context_protocol_loading_content()

    return f"""# Cliplin Project Instructions for Gemini CLI

This file contains the rules and protocols that Gemini CLI should follow when working on this Cliplin project.

## How to Use This File

- Run `gemini` from this project root so the CLI discovers `.gemini/settings.json` and this `GEMINI.md` as hierarchical context.
- Ensure that `.gemini/settings.json` contains an MCP server named `cliplin-context` pointing to `uv run cliplin mcp` (managed by `cliplin init --ai gemini`).
- Keep this file in the project so Gemini can always load the same rules and conventions when assisting on this repository.

---

{context_content}

---

{feature_first_flow_content}

---

{feature_content}

---

{protocol_content}
"""


def get_claude_desktop_claude_md_content() -> str:
    """Get the claude.md content for Claude Desktop directory."""
    return """# Claude Desktop Configuration for Cliplin

This directory contains rules and instructions for using Claude Desktop with this Cliplin project. Rules are loaded from `.claude/rules/`.

## Files

- **`.mcp.json`** (at project root): MCP server configuration for Cliplin context access
- **`instructions.md`**: Consolidated instructions file with all project rules (LOAD THIS FIRST)
- **`rules/context.md`**: Context indexing rules and context store collection mappings
- **`rules/feature-first-flow.md`**: Feature-first flow (spec before code); feature file as source of truth
- **`rules/feature-processing.md`**: Feature file processing and implementation rules
- **`rules/context-protocol-loading.md`**: Context loading protocol rules

## How to Load Rules in Claude Desktop

### Option 1: Load Instructions File (Recommended)

At the start of each conversation, copy and paste the contents of `instructions.md` into Claude Desktop. This will load all project rules at once.

### Option 2: Create a Claude Skill (Advanced)

You can create a Claude Skill from the `.claude` directory:

1. Zip the `.claude` directory (MCP config is at project root in `.mcp.json`, not inside `.claude`)
2. In Claude Desktop, go to **Settings > Extensions**
3. Click "Advanced Settings" and find "Extension Developer"
4. Click "Install Extension..." and select the ZIP file
5. Claude will automatically apply these rules in relevant contexts

### Option 3: Reference Individual Rule Files

Reference files under `.claude/rules/` as needed:
- For context loading: reference `rules/context-protocol-loading.md`
- For feature work: reference `rules/feature-processing.md`
- For indexing: reference `rules/context.md`

## MCP Server Configuration

The `.mcp.json` file at the project root configures the Cliplin context MCP server. This allows Claude to:
- Query project context from the context store collections (via Cliplin MCP)
- Access ADRs, features, TS4 specs, and UI Intent files from `docs/` and `.cliplin/knowledge/**` (built-in framework + knowledge packages)
- Load relevant context before starting any task

Make sure the MCP server is properly configured in Claude Desktop's settings to use the project's `.mcp.json`.

## Important Notes

- **Always load context first**: Before any coding, debugging, or implementation task, query the context store collections via the Cliplin MCP server
- **Follow the protocol**: The context loading protocol is mandatory and prevents wasted tokens and misaligned code
- **Update rules**: If you modify any rule files in `.claude/rules/`, reload them in Claude Desktop

For more information about Cliplin, see the main project README.
"""

