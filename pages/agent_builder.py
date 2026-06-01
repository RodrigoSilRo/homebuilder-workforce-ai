import streamlit as st

st.title("🔧 Agent Builder")
st.caption("Define a new AI agent by specifying its role, tools, data sources, and governance rules. Configurations are stored and used by the generic agent runner.")
st.markdown("---")

if "saved_agents" not in st.session_state:
    st.session_state.saved_agents = [
        {
            "name": "Vendor Risk Review Agent",
            "function": "Procurement",
            "persona": "Procurement Risk Analyst",
            "trigger": "New vendor request submitted",
            "tools": ["get_vendor_profile", "get_vendor_risk_score", "create_approval_request"],
            "data_sources": ["vendors", "policies"],
            "approval_rule": "Required for contracts > $50,000",
            "escalation_rule": "Escalate if pending approval > 24 hours",
            "safety_rule": "Do not approve vendors with missing or expired insurance",
            "output_format": "Structured JSON with vendor summary, risk assessment, and recommendation",
            "version": "1.0",
            "status": "active",
        },
    ]

left, right = st.columns([2, 3], gap="large")

with left:
    st.subheader("Define New Agent")

    with st.form("agent_builder_form", clear_on_submit=True):
        name = st.text_input("Agent Name *", placeholder="e.g. Permit Delay Monitor")
        function = st.selectbox(
            "Business Function *",
            ["Procurement", "Finance", "Operations", "Sales", "Marketing", "HR", "Legal", "Compliance", "IT"],
        )
        persona = st.text_input("Persona / Role", placeholder="e.g. Operations Risk Analyst")
        trigger = st.text_input("Trigger", placeholder="e.g. Permit status changes to 'delayed'")

        all_tools = [
            "get_community_metrics", "get_inventory_status", "get_lead_conversion",
            "get_construction_delays", "calculate_incentive_impact", "get_vendor_profile",
            "get_vendor_risk_score", "get_policy_workflow", "create_approval_request",
            "generate_marketing_campaign", "create_executive_report",
        ]
        tools = st.multiselect("Allowed Tools", all_tools)

        data_sources = st.multiselect(
            "Data Sources",
            ["communities", "homes", "leads", "vendors", "policies", "construction_delays", "marketing_campaigns"],
        )

        approval_rule = st.text_input(
            "Human Approval Rule",
            placeholder="e.g. Required when contract value > $25,000",
        )
        escalation_rule = st.text_input(
            "Escalation Rule",
            placeholder="e.g. Escalate if pending > 48 hours",
        )
        safety_rule = st.text_input(
            "Safety Rule",
            placeholder="e.g. Never approve without valid insurance on file",
        )
        output_format = st.selectbox(
            "Output Format",
            ["Structured JSON", "Executive Summary", "Checklist", "Table", "Free Text"],
        )

        submitted = st.form_submit_button("Save Agent Configuration", type="primary", use_container_width=True)

        if submitted:
            if not name or not function:
                st.error("Agent Name and Business Function are required.")
            else:
                new_agent = {
                    "name": name,
                    "function": function,
                    "persona": persona or "AI Agent",
                    "trigger": trigger or "Manual trigger",
                    "tools": tools,
                    "data_sources": data_sources,
                    "approval_rule": approval_rule or "None defined",
                    "escalation_rule": escalation_rule or "None defined",
                    "safety_rule": safety_rule or "None defined",
                    "output_format": output_format,
                    "version": "1.0",
                    "status": "active",
                }
                st.session_state.saved_agents.append(new_agent)
                st.success(f"Agent '{name}' saved successfully.")

with right:
    st.subheader("Saved Agent Configurations")

    for i, agent in enumerate(st.session_state.saved_agents):
        with st.expander(f"**{agent['name']}** — {agent['function']} · v{agent['version']}", expanded=(i == 0)):
            r1, r2 = st.columns(2)
            with r1:
                st.markdown(f"**Persona:** {agent['persona']}")
                st.markdown(f"**Trigger:** {agent['trigger']}")
                st.markdown(f"**Version:** {agent['version']}")
                st.markdown(
                    f"**Status:** <span style='color:#16a34a;font-weight:700;'>{agent['status'].upper()}</span>",
                    unsafe_allow_html=True,
                )
            with r2:
                st.markdown(f"**Approval Rule:** {agent['approval_rule']}")
                st.markdown(f"**Escalation Rule:** {agent['escalation_rule']}")
                st.markdown(f"**Safety Rule:** {agent['safety_rule']}")
                st.markdown(f"**Output Format:** {agent['output_format']}")

            if agent["tools"]:
                st.markdown("**Allowed Tools:**")
                pills = " ".join(
                    f"<span style='background:#dbeafe;color:#1d4ed8;border-radius:4px;"
                    f"padding:2px 9px;font-size:0.77rem;font-weight:600;margin:2px;'>{t}</span>"
                    for t in agent["tools"]
                )
                st.markdown(pills, unsafe_allow_html=True)

            if agent["data_sources"]:
                st.markdown("**Data Sources:**")
                ds_pills = " ".join(
                    f"<span style='background:#f3f4f6;border:1px solid #e5e7eb;border-radius:4px;"
                    f"padding:2px 9px;font-size:0.77rem;margin:2px;'>{d}</span>"
                    for d in agent["data_sources"]
                )
                st.markdown(ds_pills, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            dc1, dc2 = st.columns(2)
            with dc1:
                if st.button("Deploy to Runner", key=f"deploy_{i}", use_container_width=True, type="primary"):
                    st.success(f"'{agent['name']}' deployed to agent runner.")
            with dc2:
                if st.button("View in Marketplace", key=f"view_{i}", use_container_width=True):
                    st.switch_page("pages/agent_marketplace.py")

st.markdown("---")
st.info(
    "**Note:** In Phase 1, agent configurations are stored locally. "
    "Phase 3 (LangGraph integration) will connect these configurations to a live agent runner backed by a real LLM.",
    icon="ℹ️",
)
