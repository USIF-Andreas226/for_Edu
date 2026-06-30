import streamlit as st
from shared import ARCHITECTURES, flow_diagram, init_session_state, NODE, YELLOW, ORANGE

st.set_page_config(page_title="Agentic Architectures", page_icon="🤖", layout="wide")
init_session_state()

st.title("🤖 Kinds of Agentic Architecture")
st.caption("A visual reference for the main ways to structure AI agent systems. Use the sidebar to open a pattern.")

st.page_link("pages/0_Try_It_Yourself.py", label="🎮 Try It Yourself — simulate, build, and quiz yourself", icon="🎮")

st.markdown(
    "Agentic systems range from **a single loop** to **networks of specialized "
    "agents**. The diagram below places each pattern roughly on that spectrum — "
    "complexity and coordination overhead increase as you move right. Hover any "
    "node for its name."
)

spectrum_names = [
    "ReAct", "Reflection", "Evaluator-Optimizer", "Plan-and-Execute",
    "Sequential / Pipeline", "Router", "Orchestrator-Worker",
    "Hierarchical", "Network / Swarm",
]
spectrum_nodes = {name: (i, 0, NODE) for i, name in enumerate(spectrum_names)}
spectrum_nodes["ReAct"] = (0, 0, YELLOW)
spectrum_nodes["Network / Swarm"] = (len(spectrum_names) - 1, 0, ORANGE)
spectrum_edges = [(spectrum_names[i], spectrum_names[i + 1]) for i in range(len(spectrum_names) - 1)]

st.plotly_chart(
    flow_diagram(spectrum_nodes, spectrum_edges, height=260),
    use_container_width=True,
    config={"displayModeBar": False},
)

st.divider()
st.subheader("Compare all 10 patterns")

st.dataframe(
    {
        "Pattern": [f"{ARCHITECTURES[k]['icon']} {k}" for k in ARCHITECTURES],
        "Core idea": [ARCHITECTURES[k]["summary"][:90] + "…" for k in ARCHITECTURES],
        "Best for": [ARCHITECTURES[k]["when"] for k in ARCHITECTURES],
    },
    use_container_width=True,
    hide_index=True,
)

st.divider()
st.markdown(
    "**Rule of thumb:** start with the simplest pattern that could work (ReAct or "
    "a Router), and only add structure — planning, reflection, multiple agents, "
    "hierarchy — once a simpler version demonstrably struggles with the task. "
    "Every extra agent or loop adds latency, cost, and a new place for things to "
    "go wrong."
)

st.caption("👈 Pick an architecture in the sidebar to see its diagram, pros/cons, and a worked example.")

# ----------------------------------------------------------------------------
# Progress, tracked in st.session_state — persists as you move between pages
# within this session, resets on a fresh browser session.
# ----------------------------------------------------------------------------
st.divider()
st.subheader("Your progress")

visited = st.session_state.visited
favorites = st.session_state.favorites
total = len(ARCHITECTURES)

st.progress(
    len(visited) / total if total else 0,
    text=f"{len(visited)} / {total} patterns viewed",
)

cols = st.columns(5)
for i, key in enumerate(ARCHITECTURES):
    icon = ARCHITECTURES[key]["icon"]
    mark = "✅" if key in visited else "⬜"
    star = " ⭐" if key in favorites else ""
    with cols[i % 5]:
        st.markdown(f"{mark} {icon} {key}{star}")

if favorites:
    st.caption(f"Favorited: {', '.join(sorted(favorites))}")

if st.button("Reset progress"):
    st.session_state.visited = set()
    st.session_state.favorites = set()
    st.rerun()
