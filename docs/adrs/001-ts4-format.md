# ADR-001: TS4 Format and Usage

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
