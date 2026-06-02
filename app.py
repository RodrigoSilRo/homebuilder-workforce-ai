import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(
    page_title="HomeBuilder Workforce AI",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Database + RAG bootstrap (runs once per session) ─────────────────────────
@st.cache_resource
def bootstrap_db():
    from database.db import init_db, is_seeded
    from database.seed_data import seed_all
    init_db()
    if not is_seeded():
        seed_all()
    return True

@st.cache_resource
def bootstrap_rag():
    try:
        from services.rag_service import build_policy_index, rag_available
        if rag_available():
            build_policy_index()
    except Exception:
        pass
    return True

bootstrap_db()
bootstrap_rag()

# ── Navigation ────────────────────────────────────────────────────────────────
landing      = st.Page("pages/landing.py",             title="Home",                      icon="🏠", default=True)
exec_center  = st.Page("pages/executive_command.py",   title="Executive Command Center",  icon="⚡")
marketplace  = st.Page("pages/agent_marketplace.py",   title="Agent Marketplace",         icon="🤖")
builder      = st.Page("pages/agent_builder.py",       title="Agent Builder",             icon="🔧")
approval     = st.Page("pages/approval_queue.py",      title="Approval Queue",            icon="✅")
audit        = st.Page("pages/audit_trail.py",         title="Audit Trail",               icon="📋")
mcp          = st.Page("pages/mcp_tool_registry.py",   title="MCP Tool Registry",         icon="🔌")
monitoring   = st.Page("pages/monitoring_dashboard.py",title="Monitoring Dashboard",      icon="📊")
architecture = st.Page("pages/architecture.py",        title="Architecture",              icon="🏛️")

st.markdown("""
<style>
[data-testid="stSidebarNavItems"] { max-height: none !important; overflow: visible !important; }
[data-testid="stSidebarNavMoreItem"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

pg = st.navigation({
    "": [landing],
    "Agent Operations": [exec_center, builder, marketplace],
    "Governance": [approval, audit],
    "Platform": [mcp, monitoring, architecture],
})

st.sidebar.markdown("---")
st.sidebar.caption("HomeBuilder Workforce AI  \nBuilt by Rodrigo Rosa")

# ── Analytics ─────────────────────────────────────────────────────────────────
components.html("""
<script type="text/javascript">
    (function(c,l,a,r,i,t,y){
        c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
        t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
        y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
    })(window, document, "clarity", "script", "x0ss3zni5k");
</script>
""", height=0)

pg.run()
