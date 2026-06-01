import streamlit as st
from data.mock_data import AGENTS

st.title("🤖 Agent Marketplace")
st.caption("The AI workforce available to your organization. Each agent has a defined role, tools, and approval rules.")
st.markdown("---")

# Summary metrics
total = len(AGENTS)
active = sum(1 for a in AGENTS if a["status"] == "active")
c1, c2, c3 = st.columns(3)
c1.metric("Total Agents", total)
c2.metric("Active", active)
c3.metric("Tools Available", 11)

st.markdown("---")

# Search / filter
search = st.text_input("Search agents", placeholder="Search by name or purpose...")
filtered = [a for a in AGENTS if not search or search.lower() in a["name"].lower() or search.lower() in a["purpose"].lower()]

st.markdown("<br>", unsafe_allow_html=True)

# Agent cards — 2 per row
for i in range(0, len(filtered), 2):
    cols = st.columns(2, gap="medium")
    for j, agent in enumerate(filtered[i : i + 2]):
        with cols[j]:
            with st.container(border=True):
                h1, h2 = st.columns([1, 6])
                with h1:
                    st.markdown(f"<div style='font-size:2rem;'>{agent['icon']}</div>", unsafe_allow_html=True)
                with h2:
                    status_color = "#16a34a" if agent["status"] == "active" else "#6b7280"
                    st.markdown(
                        f"**{agent['name']}** &nbsp;"
                        f"<span style='background:{status_color};color:white;border-radius:4px;"
                        f"padding:1px 8px;font-size:0.72rem;'>{agent['status'].upper()}</span>",
                        unsafe_allow_html=True,
                    )
                    st.caption(f"Persona: {agent['persona']}")

                st.markdown(agent["purpose"])

                st.markdown("**Tools**")
                if agent["tools"]:
                    pills = " ".join(
                        f"<span style='background:#dbeafe;color:#1d4ed8;border-radius:4px;"
                        f"padding:2px 9px;font-size:0.77rem;font-weight:600;margin:2px;'>{t}</span>"
                        for t in agent["tools"]
                    )
                    st.markdown(pills, unsafe_allow_html=True)
                else:
                    st.markdown("<span style='color:#9ca3af;font-size:0.85rem;'>No direct tool calls</span>", unsafe_allow_html=True)

                if agent.get("systems"):
                    st.markdown("**Integrates with**")
                    sys_pills = " ".join(
                        f"<span style='background:#f3f4f6;border:1px solid #e5e7eb;border-radius:4px;"
                        f"padding:2px 9px;font-size:0.77rem;margin:2px;'>{s}</span>"
                        for s in agent["systems"]
                    )
                    st.markdown(sys_pills, unsafe_allow_html=True)

                st.markdown("**Approval Rules**")
                st.markdown(
                    f"<div style='color:#6b7280;font-size:0.87rem;'>{agent['approval_rules']}</div>",
                    unsafe_allow_html=True,
                )

                st.markdown("**Example prompt**")
                st.markdown(
                    f"<div style='background:#f3f4f6;border-radius:6px;padding:0.5rem 0.75rem;"
                    f"font-size:0.87rem;color:#374151;font-style:italic;'>"
                    f"&ldquo;{agent['example_prompt']}&rdquo;</div>",
                    unsafe_allow_html=True,
                )

                st.markdown("<br>", unsafe_allow_html=True)
                if st.button(f"Run {agent['name']}", key=f"run_{i}_{j}", use_container_width=True):
                    st.switch_page("pages/executive_command.py")

st.markdown("---")
st.caption("All agents route through the Critic / Governance Agent before producing a final recommendation.")
