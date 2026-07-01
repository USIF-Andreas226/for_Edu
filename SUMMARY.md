# How This App Was Built — Technical Summary

## Overview

A Streamlit multi-page app that visually teaches 10 agentic AI architecture patterns. Each pattern has a diagram, pros/cons, a worked example, code snippet, and a matching quiz.

## Architecture

```
for_Edu/
├── Home.py                          # Landing page with spectrum & progress
├── shared.py                        # Core logic: diagrams, theme, data
├── pages/
│   ├── 0_Try_It_Yourself.py         # Simulator, builder, quiz
│   ├── 1_ReAct.py                   # One-liner per pattern →
│   ├── 2_Plan_and_Execute.py        #   each calls
│   ├── 3_Reflection.py              #   render_page(key)
│   ├── 4_Orchestrator_Worker.py     #   from shared.py
│   ├── 5_Hierarchical.py
│   ├── 6_Network_Swarm.py
│   ├── 7_Sequential_Pipeline.py
│   ├── 8_Evaluator_Optimizer.py
│   ├── 9_Router.py
│   └── 10_Human_in_the_Loop.py
├── requirements.txt
├── README.md
└── SUMMARY.md
```

## Key Design Decisions

### 1. Shared Rendering (`shared.py`)
All 10 architecture pages are one-liners that delegate to `render_page(key)`. The `ARCHITECTURES` dict holds all data (nodes, edges, descriptions, code samples), keeping everything DRY.

### 2. Plotly Flow Diagrams
`flow_diagram()` renders nodes as scatter markers + edges as arrows with annotations. Each node tuple is `(x, y, color, shape?)`. Edge tuples are `(src, dst, label?, dashed?)`.

- **Dashed edges** (loopback/feedback): use `if not dashed:` to avoid a solid arrow shaft overlaying the dashed scatter line.
- **Node shapes**: `"diamond"` for the Router via Plotly's `symbol` parameter.

### 3. Step-through Simulator
`build_step_diagram()` progressively reveals nodes: on each click it shows one more node, with the current step highlighted in red (`CURRENT`). Only edges between visible nodes are rendered.

### 4. Quiz Engine
6 scenario-to-architecture matching questions with inline feedback. Scores track in session state.

### 5. Session State
`init_session_state()` initializes `visited` (set of viewed patterns) and `favorites` (set of starred patterns). Persists across pages within a session, resets on new browser session.

### 6. Dark Theme
`inject_theme()` injects ~300 lines of CSS covering:
- Dark gradient backgrounds with elevated card surfaces
- Inter font throughout, JetBrains Mono for code
- Frosted-glass sidebar with blur
- Gradient buttons with hover lift
- Styled selects, radios, sliders, tabs, checkboxes
- Gradient progress bars, styled info/success/error/warning boxes
- Custom scrollbar, fade-up entrance animation
- Removed Streamlet's default menu and footer

Previously had a module-level guard that broke multi-page CSS persistence — removed so the theme always re-injects.

### 7. Fixed Bugs
| Issue | Fix |
|-------|-----|
| Dashed loopback edges appeared as solid | Wrapped arrow annotation in `if not dashed:` |
| HITL diagram missing rejection path | Added `("Human", "Agent drafts", "request changes", True)` |
| Theme disappeared on page switch | Removed `_THEME_INJECTED` module guard — always inject CSS |
| `use_container_width` deprecated | Replaced with `width="stretch"` across all 3 files |

## Data Model

Each architecture entry in `ARCHITECTURES`:

```python
{
    "icon": str,           # emoji
    "summary": str,        # one-paragraph description
    "nodes": dict,         # {name: (x, y, color, shape?)}
    "edges": list,         # [(src, dst, label?, dashed?)]
    "example_title": str,
    "example_nodes": dict, # same format as nodes
    "example_edges": list, # same format as edges
    "when": str,           # when-to-use guidance
    "pros": [str],         # list of pros
    "cons": [str],         # list of cons
    "example": str,        # short example description
    "use_case": str,       # detailed use case
    "code": str,           # Python code sample
    "tools": str,          # tooling reference
}
```

## Color Mapping

| Constant | Hex | Role |
|----------|-----|------|
| `NODE`   | `#8899B0` | Default node |
| `YELLOW` | `#D4A017` | Action / decision |
| `GREEN`  | `#5BBF6A` | Success / output |
| `BLUE`   | `#3B82F6` | Planner / human |
| `PINK`   | `#D4507A` | Critique / evaluator |
| `PURPLE` | `#8B4FEA` | Top-level manager |
| `ORANGE` | `#CC7A00` | Swarm peer |
| `CURRENT`| `#E53935` | Simulator highlight |
