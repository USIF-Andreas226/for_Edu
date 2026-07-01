import streamlit as st
from shared import (
    ARCHITECTURES, flow_diagram, build_step_diagram, init_session_state,
    QUIZ_QUESTIONS, NODE, GREEN, YELLOW,
)

st.set_page_config(page_title="Try It Yourself", page_icon="🎮", layout="wide")
init_session_state()

st.title("🎮 Try It Yourself")
st.caption("Hands-on ways to build intuition for each pattern — click through, build your own, or test yourself.")

tab1, tab2, tab3 = st.tabs([
    "🎬 Step-through Simulator", "🛠️ Build Your Own", "🧠 Quiz: Match the Scenario",
])

# ----------------------------------------------------------------------------
# TAB 1 — Step-through simulator: walk a worked example one node at a time
# ----------------------------------------------------------------------------
with tab1:
    st.subheader("Watch a pattern execute, one step at a time")
    sim_key = st.selectbox("Pick an architecture", list(ARCHITECTURES.keys()), key="sim_choice")
    data = ARCHITECTURES[sim_key]
    names = list(data["example_nodes"].keys())

    state_key = f"step_{sim_key}"
    if state_key not in st.session_state:
        st.session_state[state_key] = 0
    step = min(st.session_state[state_key], len(names) - 1)

    col_a, col_b, col_c = st.columns([1, 1, 3])
    with col_a:
        if st.button("⏮️ Reset", key=f"reset_{sim_key}"):
            st.session_state[state_key] = 0
            st.rerun()
    with col_b:
        if st.button("▶️ Next step", key=f"next_{sim_key}", disabled=step >= len(names) - 1):
            st.session_state[state_key] = step + 1
            st.rerun()
    with col_c:
        st.caption(f"Step {step + 1} of {len(names)}: **{names[step]}**")

    fig = build_step_diagram(data["example_nodes"], data["example_edges"], step)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    if step >= len(names) - 1:
        st.success(f"Done! {data['example']}")
    else:
        st.info("Click **Next step** to advance the trace and watch the diagram grow.")

# ----------------------------------------------------------------------------
# TAB 2 — Build your own: type stages/workers/branches, see it diagrammed live
# ----------------------------------------------------------------------------
with tab2:
    st.subheader("Build a custom diagram and see it update instantly")
    builder_type = st.radio(
        "What do you want to build?",
        ["Sequential pipeline", "Orchestrator with workers", "Router with branches"],
        horizontal=True, key="builder_type",
    )

    if builder_type == "Sequential pipeline":
        st.caption("Type your pipeline stages, separated by commas.")
        raw = st.text_input("Pipeline stages", value="Input, Parse, Transform, Validate, Output", key="seq_stages")
        stage_names = [s.strip() for s in raw.split(",") if s.strip()]
        if len(stage_names) < 2:
            st.warning("Add at least 2 stages, separated by commas.")
        else:
            nodes = {name: (i, 0, GREEN if i == len(stage_names) - 1 else NODE)
                     for i, name in enumerate(stage_names)}
            edges = [(stage_names[i], stage_names[i + 1]) for i in range(len(stage_names) - 1)]
            st.plotly_chart(flow_diagram(nodes, edges), width="stretch", config={"displayModeBar": False})
            st.caption(
                f"This is a **Sequential / Pipeline** architecture with {len(stage_names)} fixed stages — "
                "see that page in the sidebar for pros, cons, and when to use it."
            )

    elif builder_type == "Orchestrator with workers":
        n_workers = st.slider("Number of worker agents", min_value=2, max_value=6, value=3, key="orch_n")
        raw = st.text_input("Worker names (comma-separated, optional)", value="", key="orch_names")
        custom_names = [s.strip() for s in raw.split(",") if s.strip()]
        worker_names = (custom_names + [f"Worker {i + 1}" for i in range(n_workers)])[:n_workers]
        nodes = {"Orchestrator": ((n_workers - 1) / 2, 1, GREEN)}
        for i, w in enumerate(worker_names):
            nodes[w] = (i, 0, NODE)
        edges = [("Orchestrator", w) for w in worker_names]
        st.plotly_chart(flow_diagram(nodes, edges), width="stretch", config={"displayModeBar": False})
        st.caption(
            f"This is an **Orchestrator-Worker** architecture with {n_workers} workers — "
            "see that page in the sidebar for pros, cons, and when to use it."
        )

    else:  # Router with branches
        st.caption("Type your branch categories, separated by commas.")
        raw = st.text_input("Branch categories", value="Billing, Technical, General", key="router_branches")
        branches = [s.strip() for s in raw.split(",") if s.strip()]
        if len(branches) < 2:
            st.warning("Add at least 2 branches, separated by commas.")
        else:
            n = len(branches)
            nodes = {"Request": (0, 0, NODE), "Router": (1, 0, YELLOW, "diamond")}
            edges = [("Request", "Router")]
            for i, b in enumerate(branches):
                y = (n - 1) / 2 - i
                nodes[b] = (2, y, NODE)
                edges.append(("Router", b))
            st.plotly_chart(flow_diagram(nodes, edges), width="stretch", config={"displayModeBar": False})
            st.caption(
                f"This is a **Router (Conditional Dispatch)** architecture with {n} branches — "
                "see that page in the sidebar for pros, cons, and when to use it."
            )

# ----------------------------------------------------------------------------
# TAB 3 — Quiz: match the scenario to the right architecture
# ----------------------------------------------------------------------------
with tab3:
    st.subheader("Match the scenario to the right architecture")
    st.caption("Pick the pattern that best fits each scenario below. Score updates as you go.")

    score = 0
    answered = 0
    for i, q in enumerate(QUIZ_QUESTIONS):
        st.markdown(f"**{i + 1}. {q['scenario']}**")
        choice = st.radio(
            "Your answer:", q["options"], key=f"quiz_{i}",
            index=None, label_visibility="collapsed",
        )
        if choice is not None:
            answered += 1
            if choice == q["answer"]:
                score += 1
                st.success("Correct!")
            else:
                st.error(f"Not quite — the best fit is **{q['answer']}**.")
        st.divider()

    progress_note = f"  ({answered}/{len(QUIZ_QUESTIONS)} answered)" if answered < len(QUIZ_QUESTIONS) else "  🎉 all answered"
    st.subheader(f"Score: {score} / {len(QUIZ_QUESTIONS)}{progress_note}")
    if st.button("Reset quiz"):
        for i in range(len(QUIZ_QUESTIONS)):
            st.session_state.pop(f"quiz_{i}", None)
        st.rerun()
