# UI Intent Schema

## Overview

The **UI Intent Schema** is a declarative YAML format designed to describe user interfaces with **preserved semantic intent**. Unlike visual design tools that focus on pixel-perfect positioning, this schema emphasizes:

- **Semantic meaning** over visual appearance
- **Layout relationships** over absolute coordinates
- **Intent preservation** across different render contexts
- **State-driven behavior** rather than timeline animations

This document provides a complete reference to the schema structure, all available fields, and their usage.

## Schema Structure

The UI Intent specification consists of five main sections:

```yaml
structure:          # Component hierarchy and layout
semantics:          # Meaning and accessibility information
state_model:        # Interactive states and transitions
motion:             # State-driven visual effects
constraints:        # Behavioral rules
annotations:        # Design rationale and notes
```

---

## 1. Structure Section

The `structure` section defines the component hierarchy and their layout specifications.

### 1.1 Components Array

Each component in the `components` array represents a UI element.

```yaml
structure:
  components:
    - id: string                    # Unique identifier (required)
      type: NodeType                # Component type (required)
      layout: LayoutSpec            # Layout specification (required)
      children?: string[]           # Array of child component IDs (optional)
      content?: string              # Text content (optional, for text-based components)
      attributes?: Record<string, any>  # HTML attributes (optional)
```

#### Component Types (NodeType)

The following component types are provided as defaults:

| Type | Description | Typical Use |
|------|-------------|-------------|
| `container` | Grouping/layout element | Wrappers, sections, divs |
| `text` | Static text display | Headings, paragraphs, labels |
| `input` | Single-line text input | Form fields, search bars |
| `textarea` | Multi-line text input | Message boxes, comments |
| `select` | Dropdown selection | Form selects, filters |
| `button` | Clickable button | Actions, submissions |
| `checkbox` | Boolean checkbox | Settings, options |
| `radio` | Radio button | Single-choice selections |
| `label` | Form label | Field labels, captions |
| `icon` | Icon/glyph | Visual indicators |
| `image` | Image display | Photos, illustrations |
| `link` | Hyperlink | Navigation, external links |

**Design System Integration**: The component types listed above can be **extended or replaced** by the components available in the project's design system. When a design system is configured, users can reference any component from their design system library using the `type` field. The design system components take precedence over the default types, allowing the UI Intent to leverage the full component library of the chosen design system while preserving semantic intent.

### 1.2 Layout Specification (LayoutSpec)

The `layout` object defines how a component is positioned and sized within its parent or canvas.

```yaml
layout:
  anchor?: Anchor              # Positioning anchor (optional)
  width?: DimensionValue       # Width specification (optional)
  height?: DimensionValue      # Height specification (optional)
  x?: number                   # X coordinate (optional)
  y?: number                   # Y coordinate (optional)
  zIndex?: number              # Stacking order (optional)
  padding?: PaddingSpec        # Internal spacing (optional)
  margin?: MarginSpec          # External spacing (optional)
```

#### Anchor Values

An `anchor` defines how a component is positioned relative to its container:

| Anchor | Behavior |
|--------|----------|
| `top` | Align to top edge |
| `bottom` | Align to bottom edge |
| `left` | Align to left edge |
| `right` | Align to right edge |
| `center` | Center horizontally and vertically |
| `fill` | Fill entire container (ignores x/y) |

**Positioning Rules:**
- **Root node with anchor**: Position calculated from anchor, `x/y` are ignored
- **Root node without anchor**: `x/y` are absolute canvas coordinates
- **Child node with anchor**: Position calculated relative to parent using anchor
- **Child node without anchor**: `x/y` are relative to parent's top-left corner

#### Dimension Values

Width and height can be specified in multiple ways:

| Value Type | Example | Description |
|------------|---------|-------------|
| Number | `200` | Fixed pixels |
| Viewport Width | `"100vw"` | 100% of viewport width |
| Viewport Height | `"100vh"` | 100% of viewport height |
| Percentage | `"50%"` | 50% of parent/canvas |
| Fill | `"fill"` | Expand to fill available space |
| Fixed | `"fixed"` | Use default fixed size |

#### Padding and Margin

```yaml
padding:
  top?: number
  right?: number
  bottom?: number
  left?: number

margin:
  top?: number
  right?: number
  bottom?: number
  left?: number
```

#### Z-Index

The `zIndex` field controls the stacking order of overlapping components. Higher values render on top.

### 1.3 Content

Text-based components (text, input, textarea, button, label, link) can have a `content` field:

```yaml
content: "Button Text"
```

### 1.4 Attributes

HTML attributes for form inputs and interactive elements:

```yaml
attributes:
  placeholder: "Enter text..."    # For input/textarea
  href: "https://example.com"     # For link
  checked: true                    # For checkbox/radio
  disabled: false                  # For form controls
  type: "email"                    # For input type
```

---

## 2. Semantics Section

The `semantics` section provides accessibility and meaning information for components. It's a dictionary keyed by component ID.

```yaml
semantics:
  component_id:
    role?: string           # Semantic role (e.g., "primary_action", "navigation")
    label?: string          # Human-readable label
    ariaLabel?: string      # ARIA label for screen readers
    description?: string    # Extended description
```

**Common Roles:**
- `primary_action`, `secondary_action`
- `primary_input`, `navigation`, `header`, `footer`
- `form_control`, `label`, `container`

---

## 3. State Model Section

The `state_model` defines interactive states and transitions. This is **semantic state**, not timeline-based animation.

```yaml
state_model:
  states: string[]              # List of possible states
  currentState: string          # Currently active state
  transitions?:                 # State transitions (optional)
    - from: string              # Source state
      to: string                # Target state
      on: string                # Trigger event (e.g., "click", "focus")
```

**Example States:**
- `idle`, `active`, `hover`, `focused`
- `loading`, `success`, `error`
- `expanded`, `collapsed`

**Design System Integration**: States can reference states defined in the project's design system. When a design system is configured, the state names used in `state_model` can correspond to states available in the design system components, allowing the UI Intent to leverage the state definitions and behaviors already established in the design system.

---

## 4. Motion Section

The `motion` section defines visual effects for each state. Effects are applied when components enter specific states.

```yaml
motion:
  state_name:
    component_id:
      opacity?: number          # 0.0 to 1.0
      borderEmphasis?: boolean  # Highlight border
      scale?: number            # Scale factor (e.g., 1.2 = 120%)
      translateX?: number       # Horizontal translation (pixels)
      translateY?: number       # Vertical translation (pixels)
      animation?: string        # Reference to design system animation preset (optional)
```

**Note**: Motion is **state-driven**, not timeline-based. Effects activate when components enter the specified state.

**Design System Integration**: Motion definitions can reference animations from the project's design system using the `animation` field. When a design system is configured, users can reference animation presets defined in their design system, which can extend or replace the individual motion properties. This allows the UI Intent to leverage the animation library and timing functions already established in the design system while maintaining state-driven behavior.

---

## 5. Constraints Section

Constraints define behavioral rules that components must follow.

```yaml
constraints:
  - id: string                  # Unique constraint ID
    target: string              # Component ID this applies to
    type: ConstraintType        # Type of constraint
    condition: string           # Condition expression
    value?: any                 # Constraint value (optional)
```

**Constraint Types:**
- `visibility`: Show/hide based on condition
- `position`: Constrain position based on condition
- `size`: Constrain size based on condition
- `relationship`: Constrain based on other components

---

## 6. Annotations Section

Annotations capture design rationale, notes, constraints, and todos. They're first-class citizens in the spec.

```yaml
annotations:
  - id: string                  # Unique annotation ID
    target: string              # Component ID this applies to
    type: AnnotationType        # Type of annotation
    content: string             # Annotation text
    position?: { x: number, y: number }  # Visual position (optional)
    visible?: boolean           # Visibility flag (optional)
```

**Annotation Types:**
- `rationale`: Design reasoning
- `note`: General notes
- `constraint`: Design constraint
- `todo`: Future work or improvements

---

## Complete Example: Chat Interface UI

Here's a complete example of a chat interface UI with detailed explanations:

```yaml
structure:
  components:
    # Main container - fills entire canvas
    - id: main_container
      type: container
      layout:
        anchor: fill              # Fill entire canvas
        width: fill               # 100% width
        height: fill              # 100% height
      children:
        - header_bar              # Header at top
        - messages_area           # Scrollable message list
        - input_container         # Input bar at bottom

    # Header bar - fixed at top
    - id: header_bar
      type: container
      layout:
        anchor: top               # Anchor to top edge
        width: fill               # Full width
        height: 60                # Fixed 60px height
      children:
        - title_text
        - status_indicator

    # Title text in header
    - id: title_text
      type: text
      layout:
        x: 20                     # 20px from left (relative to parent)
        y: 15                     # 15px from top (relative to parent)
        width: 200                # Fixed 200px width
        height: 30                # Fixed 30px height
      content: "Chat with Team"
      style:
        fontSize: 20
        fontWeight: bold
        color: "#333333"

    # Status indicator dot
    - id: status_indicator
      type: container
      layout:
        anchor: right             # Anchor to right edge of header
        x: -30                    # 30px from right edge
        y: 15                     # 15px from top
        width: 12                 # 12px circle
        height: 12
      style:
        backgroundColor: "#00ff00"
        borderRadius: 6           # Makes it circular

    # Messages area - scrollable content
    - id: messages_area
      type: container
      layout:
        x: 0                      # Start at left edge
        y: 60                     # Below header (60px)
        width: fill               # Full width
        height: fill              # Remaining height (fills space)
      children:
        - message_1
        - message_2
        - message_3

    # Individual message bubble
    - id: message_1
      type: container
      layout:
        anchor: top               # Anchor to top of messages area
        x: 20                     # 20px margin from left
        y: 20                     # 20px margin from top
        width: "70%"              # 70% of parent width
        height: 80                # Auto-height based on content
      children:
        - message_author
        - message_text

    # Message author name
    - id: message_author
      type: text
      layout:
        x: 10
        y: 5
        width: fill
        height: 20
      content: "Alice"
      style:
        fontSize: 12
        fontWeight: bold
        color: "#0066cc"

    # Message text content
    - id: message_text
      type: text
      layout:
        x: 10
        y: 25
        width: fill
        height: fill
      content: "Hey team! Let's discuss the new feature design."
      style:
        fontSize: 14
        color: "#333333"

    # Message 2 - similar structure
    - id: message_2
      type: container
      layout:
        anchor: top
        x: "30%"                  # Right-aligned (30% from left = 70% width)
        y: 110                    # Below message_1
        width: "70%"
        height: 60
      children:
        - message_2_author
        - message_2_text

    - id: message_2_author
      type: text
      layout:
        x: 10
        y: 5
        width: fill
        height: 20
      content: "Bob"
      style:
        fontSize: 12
        fontWeight: bold
        color: "#cc6600"

    - id: message_2_text
      type: text
      layout:
        x: 10
        y: 25
        width: fill
        height: fill
      content: "Sounds good! I'll prepare some mockups."

    # Message 3 - another message
    - id: message_3
      type: container
      layout:
        anchor: top
        x: 20
        y: 180
        width: "70%"
        height: 50
      children:
        - message_3_author
        - message_3_text

    - id: message_3_author
      type: text
      layout:
        x: 10
        y: 5
        width: fill
        height: 20
      content: "Alice"
      style:
        fontSize: 12
        fontWeight: bold
        color: "#0066cc"

    - id: message_3_text
      type: text
      layout:
        x: 10
        y: 25
        width: fill
        height: fill
      content: "Perfect! Looking forward to it."

    # Input container - fixed at bottom
    - id: input_container
      type: container
      layout:
        anchor: bottom            # Anchor to bottom edge
        width: fill               # Full width
        height: 80                # Fixed 80px height
      children:
        - message_input
        - send_button

    # Text input field
    - id: message_input
      type: input
      layout:
        x: 20                     # 20px from left
        y: 20                     # 20px from top (centered vertically)
        width: fill               # Fill remaining width
        height: 40                # Fixed 40px height
      attributes:
        placeholder: "Type a message..."
        type: "text"

    # Send button
    - id: send_button
      type: button
      layout:
        anchor: right             # Anchor to right edge
        x: -80                    # 80px from right (width of button)
        y: 20                     # 20px from top
        width: 60                 # Fixed 60px width
        height: 40                # Fixed 40px height
      content: "Send"
      style:
        backgroundColor: "#0066ff"
        color: "#ffffff"
        borderRadius: 4

# Semantics - Accessibility and meaning
semantics:
  main_container:
    role: chat_interface
    label: "Team chat interface"
    description: "Main chat window for team communication"
  
  header_bar:
    role: header
    label: "Chat header"
  
  title_text:
    role: heading
    label: "Chat title"
    ariaLabel: "Chat with Team"
  
  status_indicator:
    role: status_indicator
    label: "Online status"
    ariaLabel: "Team member online"
  
  messages_area:
    role: content_area
    label: "Messages"
    ariaLabel: "Chat messages"
  
  message_input:
    role: primary_input
    label: "Message input"
    ariaLabel: "Type your message here"
  
  send_button:
    role: primary_action
    label: "Send message"
    ariaLabel: "Send message to team"

# State model - Interactive states
state_model:
  states:
    - idle
    - typing
    - sending
    - sent
  currentState: idle
  transitions:
    - from: idle
      to: typing
      on: focus                    # When input is focused
    - from: typing
      to: sending
      on: click                    # When send button is clicked
    - from: sending
      to: sent
      on: success                  # When message is sent successfully
    - from: sent
      to: idle
      on: reset                    # Reset after a delay

# Motion - Visual effects for states
motion:
  typing:
    message_input:
      borderEmphasis: true         # Highlight border when typing
      borderColor: "#0066ff"
  sending:
    send_button:
      opacity: 0.7                 # Dim button while sending
      scale: 0.95                  # Slight scale down
  sent:
    send_button:
      opacity: 1.0
      scale: 1.0

# Constraints - Behavioral rules
constraints:
  - id: constraint_1
    target: messages_area
    type: visibility
    condition: "state != 'hidden'"
    value: true
  
  - id: constraint_2
    target: message_input
    type: position
    condition: "always"
    value: "bottom"                # Always at bottom

# Annotations - Design rationale
annotations:
  - id: ann_1
    target: input_container
    type: rationale
    content: "Input bar anchored to bottom for easy access on mobile devices. This follows modern chat interface patterns."
  
  - id: ann_2
    target: messages_area
    type: constraint
    content: "Messages area must be scrollable. Max height should not exceed viewport."
  
  - id: ann_3
    target: send_button
    type: note
    content: "Consider adding keyboard shortcut (Enter) to send message."
  
  - id: ann_4
    target: status_indicator
    type: todo
    content: "Implement real-time status updates via WebSocket connection."
```

---

## Key Concepts Explained

### 1. Anchor-Based Positioning

In the example above:
- `main_container` uses `anchor: fill` to fill the entire canvas
- `header_bar` uses `anchor: top` to stick to the top edge
- `input_container` uses `anchor: bottom` to stick to the bottom edge
- `send_button` uses `anchor: right` to align to the right edge

This ensures the layout adapts to different screen sizes automatically.

### 2. Relative vs Absolute Coordinates

- **Absolute coordinates** (`x: 20, y: 15`) are used for root-level components or when no anchor is set
- **Relative coordinates** are used for child components - they're relative to the parent's top-left corner
- When an `anchor` is set, `x/y` coordinates are **ignored** in favor of anchor-based positioning

### 3. Fill Dimensions

Using `width: fill` or `height: fill`:
- Makes a component expand to fill available space in its parent
- Works with anchors: `anchor: fill` + `width: fill` + `height: fill` = full container

### 4. Percentage Dimensions

Using `width: "70%"`:
- Calculates 70% of the parent's width
- Useful for responsive layouts
- Messages use 70% width to leave space for margins

### 5. Viewport Units

Using `width: "100vw"` or `height: "100vh"`:
- `100vw` = 100% of viewport width
- `100vh` = 100% of viewport height
- Useful for fullscreen components

### 6. State-Driven Motion

The `motion` section defines visual effects that activate when components enter specific states:
- When `message_input` enters `typing` state, border emphasis activates
- When `send_button` enters `sending` state, it becomes semi-transparent
- This is **semantic animation**, not timeline-based

### 7. Semantic Roles

The `semantics` section provides meaning:
- `primary_action` indicates the main action button
- `primary_input` indicates the main input field
- These roles help with accessibility and future code generation

### 8. Annotations

Annotations capture **why** design decisions were made:
- `rationale`: Explains the design reasoning
- `constraint`: Documents limitations or requirements
- `note`: General observations
- `todo`: Future improvements

---

## Best Practices

1. **Use anchors for responsive layouts**: Prefer `anchor` over fixed `x/y` when possible
2. **Separate structure from semantics**: Keep layout in `structure`, meaning in `semantics`
3. **Use semantic roles**: Always define roles for important components
4. **Document with annotations**: Capture design rationale and constraints
5. **State-driven motion**: Use `state_model` and `motion` for interactive behaviors
6. **Nest components logically**: Use parent-child relationships to group related components
7. **Preserve intent**: Write specs that communicate intent, not just appearance
8. **Leverage design system components**: When using a design system, reference its components, states, and animations to maintain consistency across the application

---

## Design System Integration

The UI Intent Schema is designed to work seamlessly with design systems. The following aspects of the schema can be extended or replaced by design system definitions:

### Component Types

The default component types (`button`, `input`, `text`, etc.) can be extended or replaced by components from your project's design system. Simply use the component names from your design system as the `type` value. For example, if your design system has a `PrimaryButton` component, you can use:

```yaml
- id: submit_btn
  type: PrimaryButton  # Uses design system component
  content: "Submit"
```

### States

State names in the `state_model` section can reference states defined in your design system components. This allows you to leverage existing state definitions and behaviors:

```yaml
state_model:
  states:
    - PrimaryButton.loading    # Reference design system state
    - PrimaryButton.success
  currentState: PrimaryButton.idle
```

### Animations

Motion definitions can reference animation presets from your design system:

```yaml
motion:
  active:
    submit_btn:
      animation: "fadeIn"  # Reference design system animation preset
```

This integration ensures that the UI Intent preserves semantic meaning while leveraging the visual consistency, component library, states, and animations of your chosen design system.

---
