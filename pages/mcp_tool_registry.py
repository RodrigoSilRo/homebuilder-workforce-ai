import streamlit as st
from data.mock_data import MCP_TOOLS
from database.db import query
from mcp_server.tool_registry import REGISTERED_TOOLS

st.title("🔌 MCP Tool Registry")
st.caption("All tools exposed via the Model Context Protocol. Connect any MCP-compatible client to call these tools directly.")
st.markdown("---")

# ── MCP Server panel ──────────────────────────────────────────────────────────
st.subheader("MCP Server")

col_info, col_config = st.columns([2, 3], gap="large")

with col_info:
    st.markdown("""
    **Server name:** `homebuilder-workforce-ai`
    **Transport:** stdio (Claude Desktop / Cursor) or HTTP
    **Tools exposed:** 11
    **Protocol:** Model Context Protocol (MCP) 1.0
    """)

    st.markdown("**Start the server:**")
    st.code("python -m mcp_server.server", language="bash")
    st.markdown("**HTTP mode (port 8000):**")
    st.code("python -m mcp_server.server --transport http --port 8000", language="bash")

with col_config:
    st.markdown("**Claude Desktop config** (`claude_desktop_config.json`):")
    import os, json
    project_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    config = {
        "mcpServers": {
            "homebuilder-workforce-ai": {
                "command": "python",
                "args": ["-m", "mcp_server.server"],
                "cwd": project_path,
            }
        }
    }
    st.code(json.dumps(config, indent=2), language="json")

st.markdown("**Compatible clients:**")
clients = ["Claude Desktop", "Cursor", "Windsurf", "Continue.dev", "Any MCP SDK client"]
cols = st.columns(len(clients))
for col, client in zip(cols, clients):
    col.markdown(
        f"<div style='background:rgba(128,128,128,0.1);border-radius:6px;padding:6px 10px;"
        f"text-align:center;font-size:0.82rem;font-weight:600;'>{client}</div>",
        unsafe_allow_html=True,
    )

st.markdown("---")

# ── Live metrics from DB ──────────────────────────────────────────────────────
@st.cache_data(ttl=10)
def load_live_metrics():
    rows = query("""
        SELECT tool_name,
               COUNT(*) AS call_count,
               AVG(latency_ms) AS avg_latency_ms,
               ROUND(100.0 * SUM(success) / COUNT(*), 1) AS success_rate,
               MAX(created_at) AS last_called
        FROM tool_calls
        GROUP BY tool_name
    """)
    return {r["tool_name"]: r for r in rows}

live = load_live_metrics()

def enrich(tool):
    m = live.get(tool["name"], {})
    return {
        **tool,
        "call_count":     m.get("call_count", tool["call_count"]),
        "avg_latency_ms": round(m.get("avg_latency_ms") or tool["avg_latency_ms"]),
        "success_rate":   m.get("success_rate", tool["success_rate"]),
        "last_called":    (m.get("last_called") or tool["last_called"])[:16],
        "mcp_registered": tool["name"] in REGISTERED_TOOLS,
    }

tools = [enrich(t) for t in MCP_TOOLS]

# ── Summary metrics ───────────────────────────────────────────────────────────
total_db_calls = sum(r["call_count"] for r in live.values()) if live else 0
avg_success    = sum(t["success_rate"] for t in tools) / len(tools)
avg_latency    = sum(t["avg_latency_ms"] for t in tools) / len(tools)
registered     = sum(1 for t in tools if t["mcp_registered"])

c1, c2, c3, c4 = st.columns(4)
c1.metric("MCP-Registered Tools", registered)
c2.metric("Total DB Calls",       f"{total_db_calls:,}")
c3.metric("Avg Success Rate",     f"{avg_success:.1f}%")
c4.metric("Avg Latency",          f"{avg_latency:.0f} ms")

st.markdown("---")

# ── Filters ───────────────────────────────────────────────────────────────────
categories = sorted({t["category"] for t in tools})
f1, f2, f3 = st.columns(3)
with f1:
    cat_f    = st.selectbox("Category", ["All"] + categories)
with f2:
    mcp_f    = st.selectbox("MCP Status", ["All", "Registered", "Not registered"])
with f3:
    search   = st.text_input("Search", placeholder="Search by name or description...")

filtered = [
    t for t in tools
    if (cat_f   == "All" or t["category"] == cat_f)
    and (mcp_f  == "All"
         or (mcp_f == "Registered" and t["mcp_registered"])
         or (mcp_f == "Not registered" and not t["mcp_registered"]))
    and (not search
         or search.lower() in t["name"].lower()
         or search.lower() in t["description"].lower())
]

st.markdown("<br>", unsafe_allow_html=True)

CATEGORY_COLORS = {
    "Sales & Operations": "rgba(37,99,235,0.1)",  "Operations": "rgba(22,163,74,0.1)",
    "Finance": "rgba(217,119,6,0.1)",              "Procurement": "rgba(124,58,237,0.1)",
    "Compliance": "rgba(220,38,38,0.1)",           "Governance": "rgba(128,128,128,0.1)",
    "Marketing": "rgba(219,39,119,0.1)",           "Reporting": "rgba(6,182,212,0.1)",
}

for tool in filtered:
    cat_bg  = CATEGORY_COLORS.get(tool["category"], "#f9fafb")
    sc      = "#16a34a" if tool["success_rate"] >= 98 else "#d97706" if tool["success_rate"] >= 95 else "#dc2626"
    is_live = tool["name"] in live
    mcp_tag = (
        " &nbsp;<span style='background:#16a34a;color:white;border-radius:4px;"
        "padding:1px 8px;font-size:0.72rem;font-weight:700;letter-spacing:0.5px;'>MCP</span>"
        if tool["mcp_registered"] else ""
    )
    live_tag = (
        " &nbsp;<span style='color:#16a34a;font-size:0.8rem;'>Live</span>"
        if is_live else ""
    )

    with st.expander(
        f"**{tool['name']}** — {tool['category']} · {tool['call_count']:,} calls · {tool['success_rate']}% success",
        expanded=False,
    ):
        lc, rc = st.columns([3, 2])

        with lc:
            st.markdown(f"**Description:** {tool['description']}")
            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown("**Input Schema**")
            for field, dtype in tool["input_schema"].items():
                st.markdown(
                    f"<code style='background:rgba(128,128,128,0.12);padding:1px 6px;border-radius:4px;'>{field}</code> "
                    f"<span style='opacity:0.55;font-size:0.87rem;'>{dtype}</span>",
                    unsafe_allow_html=True,
                )
            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown("**Output Schema**")
            for field, dtype in tool["output_schema"].items():
                st.markdown(
                    f"<code style='background:rgba(128,128,128,0.12);padding:1px 6px;border-radius:4px;'>{field}</code> "
                    f"<span style='opacity:0.55;font-size:0.87rem;'>{dtype}</span>",
                    unsafe_allow_html=True,
                )

            # MCP call example
            if tool["mcp_registered"]:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("**MCP call example**")
                example_args = list(tool["input_schema"].keys())
                example_call = {k: f"<{k}>" for k in example_args[:2]}
                st.code(
                    f"# From any MCP client:\n"
                    f"client.call_tool(\"{tool['name']}\", {example_call})",
                    language="python",
                )

        with rc:
            st.markdown(
                f"<span style='background:{cat_bg};border-radius:4px;padding:3px 10px;"
                f"font-size:0.82rem;font-weight:600;'>{tool['category']}</span>"
                + mcp_tag + live_tag,
                unsafe_allow_html=True,
            )
            st.markdown("<br>", unsafe_allow_html=True)

            m1, m2 = st.columns(2)
            m1.metric("Total Calls",  f"{tool['call_count']:,}")
            m2.metric("Avg Latency",  f"{tool['avg_latency_ms']} ms")
            st.markdown(
                f"**Success Rate:** <span style='color:{sc};font-weight:700;'>{tool['success_rate']}%</span>",
                unsafe_allow_html=True,
            )
            st.markdown(f"**Last Called:** {tool['last_called']}")

st.markdown("---")
st.info(
    "**MCP** = registered and callable via `python -m mcp_server.server`. "
    "**Live** = has real call records in the database from this session. "
    "All tool calls — from the UI, LangGraph agents, or MCP clients — are logged to the same `tool_calls` table.",
    icon="ℹ️",
)
