# Cliplin Project Instructions for Claude Desktop

This file contains all the rules and protocols that Claude should follow when working on this project.

## How to Use These Instructions

**IMPORTANT**: These instructions should be loaded at the beginning of each conversation or session. You can:
1. Copy and paste this entire file into Claude Desktop at the start of a conversation
2. Reference this file when Claude asks about project rules
3. Use the Cliplin MCP server to access project context (configured in `.mcp.json` at project root)

---

---
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


---

---
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


---

---
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
   - **Generate implementation prompt**: Ask the user if they want you to run `cliplin feature apply <feature-filepath>` to generate a structured implementation prompt that includes the feature content and implementation instructions. If the user confirms, execute the command and use the generated prompt as part of your implementation workflow

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


---

---
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

