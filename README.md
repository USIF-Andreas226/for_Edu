# Agentic Architectures

An interactive Streamlit app that visually teaches the 10 main patterns for structuring AI agent systems — from a simple ReAct loop to complex hierarchical swarms.

## Patterns Covered

| Pattern | Icon | Core Idea |
|---------|------|-----------|
| ReAct | ⚡ | Think → Act → Observe → repeat |
| Plan-and-Execute | 🗺️ | Plan first, then execute step by step |
| Reflection | 🪞 | Generate, critique, revise |
| Orchestrator-Worker | 🧩 | One orchestrator delegates to specialists |
| Hierarchical | 🏢 | Multi-level manager → worker tree |
| Network / Swarm | 🕸️ | Peer-to-peer agent collaboration |
| Sequential / Pipeline | ➡️ | Fixed linear chain of agents |
| Evaluator-Optimizer | 📊 | Generate → evaluate → iterate |
| Router | 🚦 | Classify and dispatch to one expert |
| Human-in-the-Loop | 🧑‍💻 | Pause for human approval at checkpoints |

## Features

- **Interactive diagrams** — Plotly flowcharts for each pattern with colored nodes, labeled edges, and dashed loopback arrows
- **Step-through simulator** — walk a worked example one node at a time to see the flow unfold
- **Build Your Own** — type stages, workers, or branches and see the diagram update live
- **Quiz** — 6 scenario-to-pattern matching questions with instant feedback
- **Progress tracking** — view count and favorites persist per session
- **Dark theme** — modern dark UI with gradients, glassmorphism, and hover animations

## Run It

```bash
pip install -r requirements.txt
streamlit run Home.py
```

## Project Structure

```
├── Home.py                  # Landing page with spectrum & progress
├── shared.py                # Core: diagrams, theme, architecture data, quiz
├── pages/
│   ├── 0_Try_It_Yourself.py # Simulator, builder, quiz
│   ├── 1_ReAct.py … 10_Human_in_the_Loop.py  # One file per pattern
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.10+
- streamlit
- plotly

## License

For educational use.
