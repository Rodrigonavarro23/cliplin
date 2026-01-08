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

**Note:** Cliplin tools (SPAs) are part of the Cliplin package installation, not your project directory.

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

### 4. Generate ADR Prompts

For proprietary libraries and SDKs, generate structured prompts that guide AI to create technical ADRs:

```bash
# From a local repository
cliplin adr generate ./vendor/my-proprietary-sdk

# From a remote repository (GitHub, GitLab, etc.)
cliplin adr generate https://github.com/company/proprietary-sdk
```

The command generates a structured prompt with step-by-step instructions for AI to analyze the repository and create a consistent, precise ADR following Cliplin framework standards.

### 5. Use Tools (SPAs)

Cliplin includes built-in Single Page Applications (SPAs) that you can open directly from the CLI:

```bash
# List available tools
cliplin tool --list

# Open a tool
cliplin tool ui-intent
```

**Note:** Tools are part of the Cliplin package installation, not your project. They are provided by Cliplin and available in any project where Cliplin is installed.

### 6. Work with AI

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

# Generate ADR prompt from repository
cliplin adr generate ./vendor/my-proprietary-sdk        # Local repository
cliplin adr generate https://github.com/company/sdk     # Remote repository

# Open tools (SPAs)
cliplin tool ui-intent          # Open a specific tool
cliplin tool --list             # List all available tools
```

---

## Requirements

- Python 3.10 or higher (Python 3.11 may have compatibility issues with ChromaDB on Windows)
- [uv](https://github.com/astral-sh/uv) (Astral UV) for installation
- A compatible AI assistant (Cursor, Claude Desktop, etc.)

### Windows-Specific Requirements

If you're installing Cliplin on Windows, you'll need:

1. **Microsoft Visual C++ Build Tools** (Required for ChromaDB dependency `hnswlib`)
   - Download and install from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Requires Microsoft Visual C++ 14.0 or greater
   - Without this, you'll see an error: `error: Microsoft Visual C++ 14.0 or greater is required`
   - **Important**: Install this BEFORE installing Cliplin

2. **Python Version Compatibility**
   - Recommended: Python 3.10 (most stable with ChromaDB on Windows)
   - Python 3.11 may have compatibility issues with ChromaDB
   - Verify your Python version: `python --version`

3. **Path Considerations**
   - Cliplin automatically handles Windows path compatibility
   - Use absolute paths when possible for better reliability
   - Ensure your project directory has write permissions

---

## Philosophy

> **Cliplin doesn't try to make AI smarter.  
> It makes the problem smaller, clearer, and executable.**

When problems are described correctly, both humans and AI perform better.

That's the essence of Cliplin.

---

## Ready to Get Started?

### Installation

#### For Windows Users

**Step 1: Install Prerequisites**

1. **Install Microsoft Visual C++ Build Tools** (if not already installed):
   - Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Run the installer and select "C++ build tools"
   - This is required for ChromaDB's `hnswlib` dependency

2. **Verify Python Installation**:
   ```powershell
   python --version
   # Should show Python 3.10.x (3.11 may have issues)
   ```

3. **Install uv** (if not already installed):
   ```powershell
   # With pip
   pip install uv
   
   # Or with PowerShell (recommended)
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

**Step 2: Install Cliplin**

Choose one of the installation methods below (same as other platforms).

#### Installation Methods

**Option 1: Install from PyPI (when available)**
```bash
uv tool install cliplin
```

**Option 2: Install directly from GitHub repository**
```bash
# Install from main branch
uv tool install git+https://github.com/Rodrigonavarro23/cliplin.git

# Or install from a specific branch
uv tool install git+https://github.com/Rodrigonavarro23/cliplin.git@main
```

**Option 3: Install with pip from GitHub**
```bash
pip install git+https://github.com/Rodrigonavarro23/cliplin.git
```

**Option 4: Development installation**
```bash
# Clone the repository
git clone https://github.com/Rodrigonavarro23/cliplin.git
cd cliplin

# Install in development mode
uv pip install -e .
# or
pip install -e .
```

#### Windows Installation Troubleshooting

If you encounter issues during installation:

1. **"Microsoft Visual C++ 14.0 or greater is required"**
   - Install Microsoft Visual C++ Build Tools (see Step 1 above)
   - Restart your terminal/PowerShell after installation

2. **Encoding errors when creating templates**
   - Set environment variable: `$env:PYTHONIOENCODING="utf-8"` in PowerShell
   - Or ensure your system locale supports UTF-8

3. **ChromaDB indexing fails**
   - Ensure you have write permissions in your project directory
   - Try running PowerShell/Command Prompt as Administrator
   - Check that the path length is reasonable (<260 characters recommended)

4. **Python version issues**
   - Use Python 3.10 if you encounter compatibility problems
   - Create a virtual environment: `python -m venv .venv`
   - Activate it: `.venv\Scripts\activate` (PowerShell) or `.venv\Scripts\activate.bat` (CMD)

### Initialize Your Project

After installation, initialize Cliplin in your project:

```bash
cliplin init --ai cursor
```

### Configure Claude Desktop

If you're using Claude Desktop, Cliplin creates rule files in the `.claude/` directory. To use these rules:

**Step 1: Load Instructions at the Start of Each Conversation**

At the beginning of each conversation in Claude Desktop, copy and paste the contents of `.claude/instructions.md` into the chat. This file contains all project rules consolidated in one place.

**Quick Steps:**
1. Open `.claude/instructions.md` in your editor
2. Copy the entire contents (Cmd/Ctrl + A, then Cmd/Ctrl + C)
3. Paste it into Claude Desktop at the start of your conversation
4. Claude will now follow all project rules and protocols

**Why This is Important:**
- Ensures Claude loads context from ChromaDB before any task
- Applies all technical rules and architectural constraints
- Prevents wasted tokens and misaligned code
- Maintains consistency with project specifications

**Alternative: Create a Claude Skill (Advanced)**

You can also create a Claude Skill from the `.claude/` directory for automatic rule loading:
1. Zip the `.claude/` directory (excluding `mcp_config.json`)
2. In Claude Desktop: **Settings > Extensions**
3. Click "Advanced Settings" > "Extension Developer"
4. Click "Install Extension..." and select the ZIP file
5. Claude will automatically apply these rules in relevant contexts

**Cliplin doesn't replace engineers, tools, or processes.  
It replaces ambiguity.**

---

## License

MIT

## Contributing

Contributions, issues, and feature requests are welcome. Help us make Spec-Driven Development accessible to everyone!

---

**Questions?** Open an issue or check the documentation at [docs/business/framework.md](docs/business/framework.md)
