"""Shared data and Plotly rendering logic for the Agentic Architectures app."""
import streamlit as st
import plotly.graph_objects as go

# ----------------------------------------------------------------------------
# Custom font
# ----------------------------------------------------------------------------
_CSS_INJECTED = False

def inject_custom_font() -> None:
    global _CSS_INJECTED
    if _CSS_INJECTED:
        return
    _CSS_INJECTED = True
    st.markdown("""
        <style>
        .js-plotly-plot .scatterlayer text {
            stroke: #000000 !important;
            stroke-width: 1px !important;
            paint-order: stroke fill !important;
        }
        </style>
    """, unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# Color palette (matches semantic roles across diagrams)
# Vibrant, modern palette optimized for learning engagement.
# ----------------------------------------------------------------------------
NODE = "#8899B0"        # slate gray — regular step
YELLOW = "#D4A017"       # deep golden — action / decision
GREEN = "#5BBF6A"        # emerald green — success / output
BLUE = "#3B82F6"         # vivid blue — planner / human
PINK = "#D4507A"         # deep pink — critique / evaluator
PURPLE = "#8B4FEA"       # deep violet — top-level manager
ORANGE = "#CC7A00"       # deep orange — swarm peer
CURRENT = "#E53935"      # vivid red — highlight for "current step" in the simulator


def flow_diagram(nodes: dict, edges: list, height: int = 360) -> go.Figure:

    fig = go.Figure()
    annotations = []

    for edge in edges:
        src, dst = edge[0], edge[1]
        label = edge[2] if len(edge) > 2 else None
        dashed = edge[3] if len(edge) > 3 else False
        x0, y0 = nodes[src][0], nodes[src][1]
        x1, y1 = nodes[dst][0], nodes[dst][1]
        annotations.append(dict(
            ax=x0, ay=y0, x=x1, y=y1,
            xref="x", yref="y", axref="x", ayref="y",
            showarrow=True, arrowhead=3, arrowsize=1, arrowwidth=2,
            arrowcolor="#7B8BA4",
            standoff=24, startstandoff=24,
        ))
        if label:
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            annotations.append(dict(
                x=mx, y=my, text=label, showarrow=False,
                font=dict(size=10, color="#1E293B"),
                bgcolor="rgba(255,255,255,0.92)", borderpad=2,
            ))
        if dashed:
            fig.add_trace(go.Scatter(
                x=[x0, x1], y=[y0, y1], mode="lines",
                line=dict(color="#7B8BA4", width=1.5, dash="dot"),
                hoverinfo="skip", showlegend=False,
            ))

    xs = [v[0] for v in nodes.values()]
    ys = [v[1] for v in nodes.values()]
    colors = [v[2] for v in nodes.values()]
    symbols = [v[3] if len(v) > 3 else "circle" for v in nodes.values()]
    names = list(nodes.keys())

    fig.add_trace(go.Scatter(
        x=xs, y=ys, mode="markers+text",
        marker=dict(size=55, color=colors, symbol=symbols,
                     line=dict(width=3, color="#FFFFFF")),
        text=names, textposition="bottom center",
        textfont=dict(size=10, color="#FFFFFF", family="Arial, sans-serif"),
        hoverinfo="text", hovertext=names, showlegend=False,
    ))

    fig.update_layout(
        showlegend=False,
        xaxis=dict(visible=False, range=[min(xs) - 1.2, max(xs) + 1.2]),
        yaxis=dict(visible=False, range=[min(ys) - 1.2, max(ys) + 1.0]),
        annotations=annotations,
        height=height,
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def build_step_diagram(nodes: dict, edges: list, step: int) -> go.Figure:
    """Build a partial diagram showing only nodes up to `step`, with the
    current step highlighted. Used by the step-through simulator so a user
    can click through a worked example one node at a time."""
    names = list(nodes.keys())
    step = max(0, min(step, len(names) - 1))
    visible = names[: step + 1]
    visible_set = set(visible)

    sub_nodes = {}
    for i, name in enumerate(visible):
        x, y, color, *rest = nodes[name]
        symbol = rest[0] if rest else "circle"
        if i == step:
            color = CURRENT  # highlight the current node
        sub_nodes[name] = (x, y, color, symbol)

    sub_edges = [e for e in edges if e[0] in visible_set and e[1] in visible_set]
    return flow_diagram(sub_nodes, sub_edges)


# ----------------------------------------------------------------------------
# Quiz: scenario -> best-fit architecture
# ----------------------------------------------------------------------------

QUIZ_QUESTIONS = [
    {
        "scenario": "You need an agent that debugs code by running it, reading the error, and fixing it — iterating until it works.",
        "answer": "ReAct (Reason + Act)",
        "options": ["ReAct (Reason + Act)", "Sequential / Pipeline", "Router (Conditional Dispatch)", "Hierarchical (Manager of Managers)"],
    },
    {
        "scenario": "A generator writes code, and a separate component runs the unit test suite to check correctness before anything ships.",
        "answer": "Evaluator-Optimizer",
        "options": ["Evaluator-Optimizer", "Reflection / Self-Refine", "Network / Swarm", "Plan-and-Execute"],
    },
    {
        "scenario": "A support inbox needs every incoming ticket sent to exactly one of three specialist agents based on topic.",
        "answer": "Router (Conditional Dispatch)",
        "options": ["Router (Conditional Dispatch)", "Orchestrator-Worker", "Sequential / Pipeline", "Hierarchical (Manager of Managers)"],
    },
    {
        "scenario": "The system drafts an email but must always wait for a person to click 'approve' before it actually sends.",
        "answer": "Human-in-the-Loop",
        "options": ["Human-in-the-Loop", "ReAct (Reason + Act)", "Reflection / Self-Refine", "Router (Conditional Dispatch)"],
    },
    {
        "scenario": "A document pipeline always runs the same fixed steps in order: OCR, then normalize, then extract entities, then summarize.",
        "answer": "Sequential / Pipeline",
        "options": ["Sequential / Pipeline", "Plan-and-Execute", "Network / Swarm", "Evaluator-Optimizer"],
    },
    {
        "scenario": "One orchestrator owns the overall goal and routes sub-tasks to a knowledge-extraction agent and a relationship-analysis agent, then assembles the result.",
        "answer": "Orchestrator-Worker",
        "options": ["Orchestrator-Worker", "Hierarchical (Manager of Managers)", "Network / Swarm", "Plan-and-Execute"],
    },
]


# ----------------------------------------------------------------------------
# Architecture data
# ----------------------------------------------------------------------------

ARCHITECTURES = {
    "ReAct (Reason + Act)": {
        "icon": "⚡",
        "summary": (
            "A single agent loops between *thinking* and *acting*: it reasons about "
            "the task, calls a tool, observes the result, then reasons again. The "
            "loop repeats until the agent decides it has enough to answer."
        ),
        "nodes": {
            "Thought": (0, 0, NODE),
            "Action": (1, 1, YELLOW),
            "Observation": (2, 0, NODE),
        },
        "edges": [
            ("Thought", "Action"),
            ("Action", "Observation"),
            ("Observation", "Thought", "repeat", True),
        ],
        "example_title": "Worked example: debugging a failing script",
        "example_nodes": {
            "Run the script": (0, 0, NODE),
            "Execute": (1, 1, YELLOW),
            "Stack trace": (2, 0, NODE),
            "It's a None bug": (3, 1, NODE),
            "Patch line 12": (4, 0, YELLOW),
            "Tests pass": (5, 1, NODE),
            "Done": (6, 0, GREEN),
        },
        "example_edges": [
            ("Run the script", "Execute"), ("Execute", "Stack trace"),
            ("Stack trace", "It's a None bug"), ("It's a None bug", "Patch line 12"),
            ("Patch line 12", "Tests pass"), ("Tests pass", "Done"),
        ],
        "when": "Open-ended tasks where the next step depends on what the last tool call returned (search, debugging, Q&A over tools).",
        "pros": ["Simple to implement", "Naturally handles unpredictable tool results", "Easy to debug — one trace, one agent"],
        "cons": ["Can loop too long without good stopping logic", "No separation of planning vs. doing — harder to control long-horizon tasks"],
        "example": "A coding assistant that reads an error, runs a test, reads the new error, and keeps iterating.",
        "tools": "LangGraph ReAct agent, OpenAI function calling loop",
    },
    "Plan-and-Execute": {
        "icon": "🗺️",
        "summary": (
            "A *planner* breaks the task into an explicit ordered list of steps up "
            "front. An *executor* then carries out each step, optionally re-planning "
            "if a step fails or new information changes the picture."
        ),
        "nodes": {
            "Goal": (0, 0, NODE),
            "Planner": (1, -1, BLUE),
            "Step 1": (2, 0, NODE),
            "Step 2": (3, 0, NODE),
            "Step 3": (4, 0, NODE),
            "Result": (5, 0, GREEN),
        },
        "edges": [
            ("Goal", "Planner"), ("Planner", "Step 1"), ("Step 1", "Step 2"),
            ("Step 2", "Step 3"), ("Step 3", "Result"),
            ("Step 2", "Planner", "re-plan if needed", True),
        ],
        "example_title": "Worked example: writing a research report",
        "example_nodes": {
            "Goal: EV market report": (0, 0, NODE),
            "Plan sections": (1, -1, BLUE),
            "Write intro": (2, 0, NODE),
            "Write market size": (3, 0, NODE),
            "Write players": (4, 0, NODE),
            "Write outlook": (5, 0, NODE),
            "Assemble report": (6, 0, GREEN),
        },
        "example_edges": [
            ("Goal: EV market report", "Plan sections"), ("Plan sections", "Write intro"),
            ("Write intro", "Write market size"), ("Write market size", "Write players"),
            ("Write players", "Write outlook"), ("Write outlook", "Assemble report"),
        ],
        "when": "Multi-step tasks where the full shape of the work is roughly knowable in advance (research reports, multi-stage data pipelines).",
        "pros": ["Predictable, auditable execution order", "Easier to parallelize independent steps", "Plan itself is a useful artifact to show the user"],
        "cons": ["Upfront plan can be wrong and costly to revise", "Less reactive than ReAct to surprises mid-task"],
        "example": "Generating a research report: plan sections first, then fill each one in.",
        "tools": "LangGraph plan-and-execute template, AutoGPT-style planners",
    },
    "Reflection / Self-Refine": {
        "icon": "🪞",
        "summary": (
            "After producing an output, the agent (or a second 'critic' role) reviews "
            "its own work against the goal, finds issues, and revises. Repeats for a "
            "fixed number of rounds or until the critique says 'good enough'."
        ),
        "nodes": {
            "Draft": (0, 0, NODE),
            "Critique": (1, 1, PINK),
            "Revise": (2, 0, NODE),
            "Draft v2": (3, 1, NODE),
        },
        "edges": [
            ("Draft", "Critique"), ("Critique", "Revise"), ("Revise", "Draft v2"),
            ("Draft v2", "Critique", "iterate", True),
        ],
        "example_title": "Worked example: extracting structured data",
        "example_nodes": {
            "Draft JSON": (0, 0, NODE),
            "Missing 'date' field": (1, 1, PINK),
            "Add date": (2, 0, NODE),
            "Draft v2 JSON": (3, 1, NODE),
            "Looks complete": (4, 0, PINK),
            "Return": (5, 1, GREEN),
        },
        "example_edges": [
            ("Draft JSON", "Missing 'date' field"), ("Missing 'date' field", "Add date"),
            ("Add date", "Draft v2 JSON"), ("Draft v2 JSON", "Looks complete"),
            ("Looks complete", "Return"),
        ],
        "when": "Quality-sensitive output where a second pass meaningfully improves results — writing, code review, structured extraction.",
        "pros": ["Catches errors the first pass missed", "Improves quality without new tools", "Cheap to bolt onto an existing single agent"],
        "cons": ["Doubles+ token cost per task", "Can rationalize rather than truly fix issues without a strong critic prompt"],
        "example": "An agent extracting structured data, then re-checking its own JSON against the source text before returning it.",
        "tools": "LangGraph reflection graphs, Self-Refine / Reflexion papers",
    },
    "Orchestrator-Worker": {
        "icon": "🧩",
        "summary": (
            "One orchestrator agent owns the overall goal and routes sub-tasks to "
            "specialized worker agents, each good at one narrow job. The orchestrator "
            "collects worker outputs and assembles the final result."
        ),
        "nodes": {
            "Orchestrator": (1, 1, GREEN),
            "Worker A (extract)": (0, 0, NODE),
            "Worker B (normalize)": (1, 0, NODE),
            "Worker C (analyze)": (2, 0, NODE),
        },
        "edges": [
            ("Orchestrator", "Worker A (extract)"),
            ("Orchestrator", "Worker B (normalize)"),
            ("Orchestrator", "Worker C (analyze)"),
        ],
        "example_title": "Worked example: an Arabic semantic knowledge graph pipeline",
        "example_nodes": {
            "Musghi (orchestrator)": (1, 1, GREEN),
            "Mudawin (extraction/normalization)": (0, 0, NODE),
            "Mudrik (relationship analysis)": (2, 0, NODE),
            "Final graph nodes/edges": (1, -1, GREEN),
        },
        "example_edges": [
            ("Musghi (orchestrator)", "Mudawin (extraction/normalization)"),
            ("Musghi (orchestrator)", "Mudrik (relationship analysis)"),
            ("Mudawin (extraction/normalization)", "Musghi (orchestrator)", "results", True),
            ("Mudrik (relationship analysis)", "Musghi (orchestrator)", "results", True),
            ("Musghi (orchestrator)", "Final graph nodes/edges"),
        ],
        "when": "Tasks that decompose cleanly into specialized roles, especially when each worker needs different tools, prompts, or domain knowledge.",
        "pros": ["Each worker stays simple and focused", "Easy to swap/upgrade one worker without touching others", "Scales well — this is what most production agent systems use"],
        "cons": ["Orchestrator becomes a single point of failure / bottleneck", "Coordination overhead and inter-agent message design adds complexity"],
        "example": "A knowledge-graph pipeline where an orchestrator routes raw text to an extraction agent, then a relationship-analysis agent.",
        "tools": "LangGraph supervisor pattern, CrewAI, AutoGen GroupChat",
    },
    "Hierarchical (Manager of Managers)": {
        "icon": "🏢",
        "summary": (
            "Extends orchestrator-worker to multiple levels: top-level managers "
            "delegate to mid-level managers, who delegate to leaf workers. Each "
            "layer only needs to understand the layer directly below it."
        ),
        "nodes": {
            "Top Manager": (1, 2, PURPLE),
            "Team Lead A": (0, 1, NODE),
            "Team Lead B": (2, 1, NODE),
            "Worker A1": (-0.5, 0, NODE),
            "Worker A2": (0.5, 0, NODE),
            "Worker B1": (2, 0, NODE),
        },
        "edges": [
            ("Top Manager", "Team Lead A"), ("Top Manager", "Team Lead B"),
            ("Team Lead A", "Worker A1"), ("Team Lead A", "Worker A2"),
            ("Team Lead B", "Worker B1"),
        ],
        "example_title": "Worked example: enterprise automation suite",
        "example_nodes": {
            "CEO Agent": (1, 2, PURPLE),
            "Finance Manager": (0, 1, NODE),
            "HR Manager": (2, 1, NODE),
            "Invoice Agent": (-0.5, 0, NODE),
            "Budget Agent": (0.5, 0, NODE),
            "Recruiting Agent": (2, 0, NODE),
        },
        "example_edges": [
            ("CEO Agent", "Finance Manager"), ("CEO Agent", "HR Manager"),
            ("Finance Manager", "Invoice Agent"), ("Finance Manager", "Budget Agent"),
            ("HR Manager", "Recruiting Agent"),
        ],
        "when": "Very large or organizationally complex systems with many distinct sub-domains, each itself needing coordination.",
        "pros": ["Keeps any single prompt/context small and focused", "Mirrors how large human orgs scale", "Failures isolate to a branch instead of the whole system"],
        "cons": ["Latency stacks up across layers", "Harder to debug — errors can get lost or reinterpreted between layers", "Overkill for small tasks"],
        "example": "A large enterprise automation suite where one manager handles 'finance' tasks and another handles 'HR' tasks, each with their own sub-agents.",
        "tools": "AutoGen nested teams, custom LangGraph subgraphs",
    },
    "Network / Swarm": {
        "icon": "🕸️",
        "summary": (
            "No fixed hierarchy. Agents communicate peer-to-peer, each deciding "
            "dynamically who to hand off to next based on the current state, rather "
            "than reporting back to a central orchestrator."
        ),
        "nodes": {
            "Agent A": (0, 0, ORANGE),
            "Agent B": (1, 1.5, ORANGE),
            "Agent C": (2, 0, ORANGE),
        },
        "edges": [
            ("Agent A", "Agent B"), ("Agent B", "Agent C"), ("Agent C", "Agent A"),
            ("Agent A", "Agent C"), ("Agent B", "Agent A"),
        ],
        "example_title": "Worked example: multi-agent debate",
        "example_nodes": {
            "Proposer": (0, 0, ORANGE),
            "Skeptic": (1, 1.2, ORANGE),
            "Judge": (2, 0, GREEN),
        },
        "example_edges": [
            ("Proposer", "Skeptic"),
            ("Skeptic", "Proposer", "objection", True),
            ("Skeptic", "Judge"), ("Proposer", "Judge"),
        ],
        "when": "Tasks where the right next agent genuinely depends on dynamic context and a rigid hierarchy would be artificial.",
        "pros": ["Flexible, no single bottleneck", "Can model genuinely collaborative or adversarial dynamics well"],
        "cons": ["Hardest pattern to debug and predict", "Risk of infinite hand-off loops without careful guardrails", "Least mature tooling support"],
        "example": "Multi-agent negotiation or debate setups, where agents pass the conversation back and forth until consensus.",
        "tools": "AutoGen swarm mode, OpenAI Swarm",
    },
    "Sequential / Pipeline": {
        "icon": "➡️",
        "summary": (
            "A fixed chain of agents where each one's output is the next one's "
            "input. The order is decided at design time — no agent makes routing "
            "decisions, the work just flows downstream."
        ),
        "nodes": {
            "Input": (0, 0, NODE),
            "Agent 1 (parse)": (1, 0, NODE),
            "Agent 2 (transform)": (2, 0, NODE),
            "Agent 3 (validate)": (3, 0, NODE),
            "Output": (4, 0, GREEN),
        },
        "edges": [
            ("Input", "Agent 1 (parse)"), ("Agent 1 (parse)", "Agent 2 (transform)"),
            ("Agent 2 (transform)", "Agent 3 (validate)"), ("Agent 3 (validate)", "Output"),
        ],
        "example_title": "Worked example: document processing pipeline",
        "example_nodes": {
            "Raw scan": (0, 0, NODE),
            "OCR agent": (1, 0, NODE),
            "Normalization agent": (2, 0, NODE),
            "Entity extraction agent": (3, 0, NODE),
            "Summary agent": (4, 0, NODE),
            "Final summary": (5, 0, GREEN),
        },
        "example_edges": [
            ("Raw scan", "OCR agent"), ("OCR agent", "Normalization agent"),
            ("Normalization agent", "Entity extraction agent"),
            ("Entity extraction agent", "Summary agent"), ("Summary agent", "Final summary"),
        ],
        "when": "Well-defined linear workflows where the steps are always the same and don't depend on dynamic routing (ETL-style pipelines, document processing).",
        "pros": ["Extremely simple to reason about and test", "Each stage testable in isolation", "Predictable cost and latency"],
        "cons": ["No flexibility to skip or reorder steps based on content", "A bad step poisons everything downstream with no recovery path"],
        "example": "A document pipeline: OCR agent → normalization agent → entity extraction agent → summarization agent, run in a fixed order every time.",
        "tools": "LangChain SequentialChain, plain function composition, LangGraph linear graphs",
    },
    "Evaluator-Optimizer": {
        "icon": "📊",
        "summary": (
            "A generator agent produces a candidate solution; a separate evaluator "
            "agent scores it against explicit criteria. If it fails, the feedback "
            "goes back to the generator. The loop repeats until the score passes a "
            "threshold or a max-iteration cap is hit."
        ),
        "nodes": {
            "Generator": (0, -0.5, NODE),
            "Candidate": (1, 0, NODE),
            "Evaluator": (2, -0.5, PINK),
            "Output (pass)": (3, 0.5, GREEN),
        },
        "edges": [
            ("Generator", "Candidate"), ("Candidate", "Evaluator"),
            ("Evaluator", "Output (pass)"),
            ("Evaluator", "Generator", "fail + feedback", True),
        ],
        "example_title": "Worked example: code generation with tests",
        "example_nodes": {
            "Generator: writes function": (0, 0, NODE),
            "Run unit tests": (1, 0.6, NODE),
            "2/5 tests fail": (2, 0, PINK),
            "Generator: revises": (3, 0.6, NODE),
            "Run unit tests again": (4, 0, NODE),
            "5/5 pass — ship": (5, 0.6, GREEN),
        },
        "example_edges": [
            ("Generator: writes function", "Run unit tests"),
            ("Run unit tests", "2/5 tests fail"),
            ("2/5 tests fail", "Generator: revises", "feedback: edge case missing", True),
            ("Generator: revises", "Run unit tests again"),
            ("Run unit tests again", "5/5 pass — ship"),
        ],
        "when": "Tasks with a clear, measurable quality bar — code that must pass tests, translations checked for fidelity, parameter tuning.",
        "pros": ["Clean separation of 'produce' vs. 'judge' keeps each prompt focused", "Objective stopping condition instead of a vague 'good enough'"],
        "cons": ["Only as good as the evaluator — a weak evaluator gives false confidence", "Can loop indefinitely without a hard iteration cap"],
        "example": "A code-generation agent writes a function, an evaluator runs the unit test suite, failures get sent back as feedback until tests pass.",
        "tools": "LangGraph evaluator-optimizer graphs, AlphaCodium-style test-driven loops",
    },
    "Router (Conditional Dispatch)": {
        "icon": "🚦",
        "summary": (
            "A lightweight router classifies the incoming request and dispatches it "
            "to exactly one specialized agent. No looping back, no multi-agent "
            "coordination — just 'pick the right expert and hand off'."
        ),
        "nodes": {
            "Request": (0, 0, NODE),
            "Router": (1, 0, YELLOW, "diamond"),
            "Agent A": (2, 1, NODE),
            "Agent B": (2, 0, NODE),
            "Agent C": (2, -1, NODE),
        },
        "edges": [
            ("Request", "Router"), ("Router", "Agent A"),
            ("Router", "Agent B"), ("Router", "Agent C"),
        ],
        "example_title": "Worked example: support ticket triage",
        "example_nodes": {
            "Incoming ticket": (0, 0, NODE),
            "Classify intent": (1, 0, YELLOW, "diamond"),
            "Billing agent": (2, 1, NODE),
            "Technical agent": (2, 0, NODE),
            "General agent": (2, -1, NODE),
        },
        "example_edges": [
            ("Incoming ticket", "Classify intent"),
            ("Classify intent", "Billing agent", "billing"),
            ("Classify intent", "Technical agent", "bug report"),
            ("Classify intent", "General agent", "other"),
        ],
        "when": "The front door of a system handling diverse request types where each type has one clear best-fit handler (support triage, multi-domain assistants).",
        "pros": ["Very low latency and cost — only one downstream agent runs", "Easy to extend by adding a new branch"],
        "cons": ["Misclassification sends the whole request to the wrong specialist with no recovery", "Doesn't handle requests that genuinely need more than one specialist"],
        "example": "A support system where the router reads a ticket and forwards it to a billing, technical, or general-inquiry agent.",
        "tools": "LangGraph conditional edges, OpenAI function-calling classifiers, simple intent classifiers",
    },
    "Human-in-the-Loop": {
        "icon": "🧑‍💻",
        "summary": (
            "The agent pauses at defined checkpoints and waits for explicit human "
            "approval or input before continuing, instead of running fully "
            "autonomously end-to-end."
        ),
        "nodes": {
            "Agent drafts": (0, 0, NODE),
            "Checkpoint": (1, 0, NODE),
            "Human": (2, 0, BLUE),
            "Agent continues": (3, 0, NODE),
            "Output": (4, 0, GREEN),
        },
        "edges": [
            ("Agent drafts", "Checkpoint"), ("Checkpoint", "Human"),
            ("Human", "Agent continues", "approve"), ("Agent continues", "Output"),
        ],
        "example_title": "Worked example: email-sending assistant",
        "example_nodes": {
            "Agent drafts email": (0, 0, NODE),
            "Queued for review": (1, 0, NODE),
            "Human": (2, 0, BLUE),
            "Agent sends email": (3, 0.7, GREEN),
            "Agent revises draft": (3, -0.7, PINK),
        },
        "example_edges": [
            ("Agent drafts email", "Queued for review"), ("Queued for review", "Human"),
            ("Human", "Agent sends email", "clicks approve"),
            ("Human", "Agent revises draft", "requests changes", True),
        ],
        "when": "High-stakes or irreversible actions (sending money, deleting data, publishing content) where autonomy risk outweighs speed.",
        "pros": ["Major safety and control benefit", "Builds user trust", "Lets a human correct course before any real-world damage"],
        "cons": ["Slower — doesn't scale to high request volume", "Needs a review UI/workflow built around the checkpoint"],
        "example": "An agent drafts and queues emails, but a human must click 'approve' before anything actually sends.",
        "tools": "LangGraph interrupt/checkpoint nodes, human-approval queues in Celery/Temporal workflows",
    },
}


def init_session_state() -> None:
    """Set up the session-state slots this app relies on, once per session."""
    inject_custom_font()
    if "visited" not in st.session_state:
        st.session_state.visited = set()
    if "favorites" not in st.session_state:
        st.session_state.favorites = set()


def render_page(key: str) -> None:
    """Render a full architecture page given a key into ARCHITECTURES."""
    init_session_state()
    st.session_state.visited.add(key)  # mark this pattern as seen, persists across pages

    data = ARCHITECTURES[key]

    title_col, fav_col = st.columns([5, 1])
    with title_col:
        st.title(f"{data['icon']} {key}")
    with fav_col:
        st.markdown("####")  # vertical alignment spacer
        is_fav = st.checkbox(
            "⭐ Favorite", value=key in st.session_state.favorites, key=f"fav_{key}"
        )
        if is_fav:
            st.session_state.favorites.add(key)
        else:
            st.session_state.favorites.discard(key)

    st.write(data["summary"])

    st.subheader("Structure")
    fig1 = flow_diagram(data["nodes"], data["edges"])
    st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("✅ Pros")
        for p in data["pros"]:
            st.markdown(f"- {p}")
    with col2:
        st.subheader("⚠️ Cons")
        for c in data["cons"]:
            st.markdown(f"- {c}")

    st.subheader("When to use it")
    st.info(data["when"])

    st.subheader(data["example_title"])
    fig2 = flow_diagram(data["example_nodes"], data["example_edges"])
    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
    st.caption(data["example"])

    st.subheader("Common tooling")
    st.code(data["tools"], language=None)
