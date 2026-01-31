# ADR-002: UI Intent Schema Format and Usage

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
