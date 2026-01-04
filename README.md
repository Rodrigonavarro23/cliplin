# Cliplin - Spec Driven Development Framework... *with tools*

> **Describe the problem clearly, and half of it is already solved.**  
> — *Kidlin's Law*

**Cliplin** is a command-line tool that enables **Spec-Driven Development** in your projects, taking human-AI collaboration to the next level.

---

## What is Spec-Driven Development?

**Spec-Driven Development** is a software development methodology where **specifications are the source of truth**, not code. It's similar to approaches like SpecKit, but taken to a practical operational level.

### The Problem It Solves

In modern enterprise environments, AI tools fail not because models are weak, but because:

- ❌ Context is implicit, fragmented, or inconsistent
- ❌ Technical decisions get lost in conversations or outdated documentation
- ❌ There's no single source of truth about what, how, and why to build
- ❌ AI lacks structured access to project decisions and rules

### The Solution: Specifications as Source of Truth

In Spec-Driven Development:

- ✅ **Specifications are versioned and live in the repository**
- ✅ **Code is an output of the system, not its source of truth**
- ✅ **AI only acts on well-defined specifications**
- ✅ **Every change is traceable to a specification**

---

## Cliplin: Spec-Driven Development for the AI Era

Cliplin is not just a CLI tool. It's a **complete operational framework** that implements Spec-Driven Development in real projects, with real teams and real constraints.

### The Four Pillars of Cliplin

Cliplin organizes specifications into four complementary pillars, each with a precise responsibility:

#### 1. 🎯 Business Features (.feature - Gherkin)
**Defines WHAT the system must do and WHY**

- Specifications written in Gherkin (Given-When-Then)
- Express business behavior and rules
- They are the **source of truth** of the system
- **Key principle**: If a feature doesn't exist, the functionality doesn't exist

#### 2. 🎨 UI Intent Specifications (YAML)
**Defines HOW the system expresses intent to users**

- Describe screens, components, roles, and responsibilities
- Focus on **intent**, not pixels
- Allow AI to generate UI code without guessing UX decisions

#### 3. ⚙️ TS4 - Technical Specifications (YAML)
**Defines HOW software must be implemented**

- Act as a **technical contract**
- Include: coding conventions, naming rules, validation strategies
- **Key principle**: Doesn't describe WHAT to build, defines HOW to build it correctly

#### 4. 📋 ADRs and Business Documentation (Markdown)
**Preserves WHY technical decisions were made**

- Architectural choices, trade-offs, constraints
- Prevents AI (and humans) from reopening closed decisions

---

## How Cliplin Works

### 1. Initialize Your Project

```bash
# Quick installation with uv
uv tool install cliplin

# Or one-time execution
uvx cliplin init --ai cursor
```

Cliplin automatically creates the directory structure and configures everything needed:

```
.
├── docs/
│   ├── adrs/          # Architecture Decision Records
│   ├── business/      # Business documentation
│   ├── features/       # Feature files (Gherkin)
│   ├── ts4/           # Technical specifications
│   └── ui-intent/      # UI specifications
└── .cliplin/
    ├── config.yaml
    └── data/context/   # ChromaDB database for context
```

### 2. Write Specifications

**Feature File** (`docs/features/authentication.feature`):
```gherkin
Feature: User Authentication
  As a user
  I want to log in
  So that I can access my account

  Scenario: Successful login
    Given I have valid credentials
    When I enter my email and password
    Then I should be authenticated
    And I should be redirected to the dashboard
```

**TS4 File** (`docs/ts4/input-validation.ts4`):
```yaml
ts4: "1.0"
id: "input-validation"
title: "Input Validation"
summary: "Validate data at controllers; internal services assume validity"
rules:
  - "Avoid repeating validations in internal services"
  - "Provide clear errors with 4xx HTTP status codes"
code_refs:
  - "handlers/user.py"
  - "validators/*.py"
```

### 3. Index Context

```bash
# Index all specifications
cliplin reindex

# Index a specific type
cliplin reindex --type ts4

# Preview changes
cliplin reindex --dry-run
```

Cliplin uses **ChromaDB** to semantically index and search all your specifications, enabling AI to access relevant context in real-time.

### 4. Work with AI

With Cliplin configured, you can tell your AI assistant:

> "Implement the authentication feature"

And the AI will:
1. ✅ Automatically load context from ChromaDB
2. ✅ Read the feature file and related specifications
3. ✅ Apply technical rules defined in TS4
4. ✅ Respect architectural decisions in ADRs
5. ✅ Generate code aligned with your specifications

---

## Benefits of Cliplin

### 🎯 For Teams

- **Faster onboarding**: New members understand the project through clear specifications
- **Safe parallelization**: Specifications prevent conflicts and confusion
- **Auditable decisions**: Every change is traceable to a specification
- **Preserved knowledge**: ADRs prevent reopening closed decisions

### 🤖 For AI-Assisted Development

- **Predictable behavior**: AI acts on specifications, not guessing
- **Structured context**: ChromaDB provides semantic search of specifications
- **Guaranteed consistency**: Technical rules (TS4) ensure uniform code
- **Fewer iterations**: Clear specifications reduce misunderstandings

### 📈 For Business

- **Reduced ambiguity**: Clear specifications = fewer interpretation errors
- **Complete traceability**: Every line of code traceable to a feature
- **Safer changes**: Specifications prevent unwanted changes
- **Living documentation**: Specifications are code, not obsolete documentation

---

## Key Commands

```bash
# Initialize project
cliplin init --ai cursor              # For Cursor AI
cliplin init --ai claude-desktop      # For Claude Desktop

# Validate structure
cliplin validate

# Index specifications
cliplin reindex                        # All
cliplin reindex docs/features/*.feature  # Specific
cliplin reindex --type ts4            # By type
cliplin reindex --directory docs/business  # By directory
cliplin reindex --dry-run             # Preview

# Generate implementation prompt
cliplin feature apply docs/features/my-feature.feature
```

---

## Requirements

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) (Astral UV) for installation
- A compatible AI assistant (Cursor, Claude Desktop, etc.)

---

## Philosophy

> **Cliplin doesn't try to make AI smarter.  
> It makes the problem smaller, clearer, and executable.**

When problems are described correctly, both humans and AI perform better.

That's the essence of Cliplin.

---

## Ready to Get Started?

```bash
uv tool install cliplin
cliplin init --ai cursor
```

**Cliplin doesn't replace engineers, tools, or processes.  
It replaces ambiguity.**

---

## License

MIT

## Contributing

Contributions, issues, and feature requests are welcome. Help us make Spec-Driven Development accessible to everyone!

---

**Questions?** Open an issue or check the documentation at [docs/business/framework.md](docs/business/framework.md)
