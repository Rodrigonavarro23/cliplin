# Cliplin Framework

> **Describe the problem clearly, and half of it is already solved.**
> — *Kidlin’s Law*

---

## 1. What Is Cliplin

**Cliplin** is a framework for building and maintaining software in enterprise environments using **AI-assisted development driven by specifications**.

It is designed to operate inside real-world repositories, with real teams, real constraints, and long-lived codebases.

Cliplin does **not** replace engineers, tools, or processes.
It replaces ambiguity.

At its core, Cliplin operationalizes **Kidlin’s Law**:

> If the problem is described clearly, execution becomes repetible — for humans and for AI.

---

## 2. The Core Idea

Modern AI tools fail in enterprise settings not because models are weak, but because **context is implicit, fragmented, or inconsistent**.

Cliplin solves this by enforcing a simple but strict rule:

> **AI is only allowed to act on well-defined, versioned specifications that live in the repository.**

Code becomes an output of the system — not its source of truth.

---

## 3. The Four Pillars of Cliplin

Cliplin is built on **four complementary specification pillars**, each with a precise responsibility.

### 3.1 Business Features (.feature files – Gherkin)

**Purpose:** Define *what* the system must do and *why*.

* Written in Gherkin
* Express business behavior and rules
* Represent the **source of truth** of the system

**Key principle:**

> If a feature does not exist, the functionality does not exist.

---

### 3.2 UI Intent Specifications (YAML)

**Purpose:** Define *how the system expresses intent to users*, beyond visual design.

* Describe screens, components, roles, and responsibilities
* Assume the existence of a design system (generic or custom)
* Focus on **intent**, not pixels

These specs allow AI to generate UI code without guessing user experience decisions.

---

### 3.3 TS4 – Technical Specification Files (YAML)

**Purpose:** Define *how software must be implemented*.

TS4 files act as a **technical contract** and include:

* Coding conventions
* Naming rules
* Validation strategies
* Allowed and forbidden patterns
* Project-specific technical decisions

**Key principle:**

> TS4 does not describe what to build. It defines how to build it correctly.

---

### 3.4 Architecture Decision Records and business documentation (ADRs and mds)

**Purpose:** Preserve *why technical decisions were made*.

* Architecture choices
* Trade-offs
* Constraints and irreversible decisions
* Business descriptions
* Environment considerations

ADRs prevent AI (and humans) from reopening closed decisions or proposing invalid architectures.

---

## 4. Cliplin as an Operational Model

Cliplin is not just documentation — it is an **operational model**.

### Inputs

Only the following are valid inputs:

* Business Features (.feature)
* UI Intent specifications
* TS4 technical rules
* ADRs and business documentation

Anything else is noise.

---

### Constraints

Cliplin works by **deliberate limitation**:

* Business constraints (Features)
* Semantic constraints (UI Intent)
* Technical constraints (TS4)
* Architectural constraints (ADRs)

Creativity is replaced by clarity.

---

### Outputs

Expected outputs are:

* Business-aligned code
* Tests derived from scenarios
* UI consistent with intent
* Architecture-compliant changes

Every output must be traceable back to a specification.

---

## 5. Working With Features as the Orchestration Layer

In Cliplin, `.feature` files are not passive documentation — they **orchestrate execution**.

### Feature Lifecycle via Tags

Features use semantic tags to express state and evolution:

* `@status:pending` or without tag – not implemented
* `@status:implemented` – implemented and active
* `@status:deprecated` – must not be modified

Change tracking:

* `@changed:YYYY-MM-DD`
* `@reason:<short description>`

These tags allow commands like:

> **“Implement or adjust feature X”**

To be executed autonomously and safely.

---

## 6. Why Cliplin Works in Enterprise Environments

Cliplin is designed for:

* Teams
* Parallel feature development
* Long-lived repositories
* High onboarding and turnover costs

Benefits:

* Reduced ambiguity
* Predictable AI behavior
* Faster onboarding
* Smaller, safer changes
* Auditable decisions

---

## 7. What Cliplin Is Not

* Not a code generator
* Not a prompting technique
* Not a replacement for engineering judgment
* Not tied to a specific AI tool

Cliplin is a **problem-reduction system**.

---

## 8. Final Statement

Cliplin does not aim to make AI smarter.

It makes the **problem smaller, clearer, and executable**.

When problems are described properly, both humans and AI perform better.

That is the essence of Cliplin.

---

## 9. Context Access via MCP (Model Context Protocol)

Cliplin exposes the context store to AI tools (e.g. Cursor, Claude Desktop) via the **Model Context Protocol (MCP)**. This allows the AI to query indexed specifications semantically without opening every file.

### How the MCP server is started

- **Configuration**: The host (Cursor, Claude Desktop, etc.) reads a config file (e.g. `.cursor/mcp.json`) that declares available MCP servers and how to run them.
- **Command**: For Cliplin, the server is started by running `cliplin mcp` (or the configured command). The host launches this process and communicates over **stdio** (stdin/stdout); no network port is used.
- **Working directory**: The host typically starts the process with the **project root** as the current working directory. Cliplin assumes `cwd` is the project root when resolving paths (e.g. `.cliplin/data/context/`, `docs/ts4/`).
- **Clean stdio**: The `cliplin mcp` command must not print banners, help text, or any extra output to stdout. Only MCP protocol messages go over stdio; any other output would break the protocol.
- **Server instructions**: The MCP server must expose **instructions** (a short description of its purpose and how to use it) in the MCP handshake. Without this, some hosts (e.g. Cursor) send GetInstructions, get no usable response, and log "No server info found." The server must always return both serverInfo and instructions so that the host can display the server correctly and the AI knows how to use it.

### Role of the context server

The MCP server exposes tools such as: list collections, query documents by semantic search, add/update/delete documents, and check whether documents have changed (fingerprint store). These tools allow the AI to load relevant context (ADRs, features, TS4, UI intent) before answering or generating code, in line with the rule *"Never proceed without context."*

### Supported hosts and config consistency

Supported AI hosts include **Cursor** (`.cursor/mcp.json`) and **Claude Desktop** (`.claude/mcp_config.json`). When changing how the MCP server is started (e.g. command or args in init templates), the same command must be used for all hosts so that every host runs the project's Cliplin with the same behavior. See `docs/ts4/ai-host-integration.ts4` for technical rules and the checklist when modifying templates or MCP-related commands.
