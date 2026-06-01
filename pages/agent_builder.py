import json
import streamlit as st
from database.db import query, execute

st.title("🔧 Agent Builder")
st.caption("Define a new AI agent by specifying its role, tools, data sources, and governance rules. Configurations are saved to the database.")
st.markdown("---")


@st.cache_data(ttl=5)
def load_agents():
    rows = query("SELECT * FROM agent_configs ORDER BY id")
    result = []
    for r in rows:
        result.append({
            "id":             r["id"],
            "name":           r["name"],
            "function":       r.get("business_function") or "",
            "persona":        r.get("persona") or "AI Agent",
            "trigger":        r.get("trigger_description") or "Manual trigger",
            "tools":          json.loads(r.get("allowed_tools_json") or "[]"),
            "approval_rule":  r.get("approval_rule") or "None defined",
            "escalation_rule":r.get("escalation_rule") or "None defined",
            "safety_rule":    r.get("safety_rule") or "None defined",
            "output_format":  r.get("output_format") or "Free Text",
            "version":        r.get("version") or "1.0",
            "status":         "active" if r.get("active", 1) else "inactive",
        })
    return result


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
                execute("""
                    INSERT INTO agent_configs
                      (name, business_function, persona, trigger_description, allowed_tools_json,
                       approval_rule, escalation_rule, safety_rule, output_format, version, active)
                    VALUES
                      (:name, :func, :persona, :trigger, :tools,
                       :appr, :esc, :safety, :fmt, '1.0', 1)
                """, {
                    "name":    name,
                    "func":    function,
                    "persona": persona or "AI Agent",
                    "trigger": trigger or "Manual trigger",
                    "tools":   json.dumps(tools),
                    "appr":    approval_rule or "None defined",
                    "esc":     escalation_rule or "None defined",
                    "safety":  safety_rule or "None defined",
                    "fmt":     output_format,
                })
                st.cache_data.clear()
                st.success(f"Agent '{name}' saved to database.")

with right:
    st.subheader("Saved Agent Configurations")

    saved_agents = load_agents()

    if not saved_agents:
        st.info("No agent configurations found.")
    else:
        for agent in saved_agents:
            with st.expander(f"**{agent['name']}** — {agent['function']} · v{agent['version']}", expanded=False):
                r1, r2 = st.columns(2)
                with r1:
                    st.markdown(f"**Persona:** {agent['persona']}")
                    st.markdown(f"**Trigger:** {agent['trigger']}")
                    st.markdown(f"**Version:** {agent['version']}")
                    status_color = "#16a34a" if agent["status"] == "active" else "#6b7280"
                    st.markdown(
                        f"**Status:** <span style='color:{status_color};font-weight:700;'>{agent['status'].upper()}</span>",
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
                        f"<span style='background:rgba(27,82,153,0.1);color:var(--primary-color);border-radius:4px;"
                        f"padding:2px 9px;font-size:0.77rem;font-weight:600;margin:2px;'>{t}</span>"
                        for t in agent["tools"]
                    )
                    st.markdown(pills, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                dc1, dc2 = st.columns(2)
                with dc1:
                    if st.button("Deploy to Runner", key=f"deploy_{agent['id']}", use_container_width=True, type="primary"):
                        execute(
                            "UPDATE agent_configs SET active=1 WHERE id=:id",
                            {"id": agent["id"]},
                        )
                        st.cache_data.clear()
                        st.success(f"'{agent['name']}' is active in the registry.")
                with dc2:
                    if st.button("View in Marketplace", key=f"view_{agent['id']}", use_container_width=True):
                        st.switch_page("pages/agent_marketplace.py")

st.markdown("---")
