import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database.db import query
from services.eval_service import run_all_evals, get_eval_history, get_eval_drift

st.title("📊 Monitoring Dashboard")
st.caption("Real-time agent health, tool performance, approval rates, eval results, and drift detection — all sourced live from the database.")
st.markdown("---")

# ── Live data ─────────────────────────────────────────────────────────────────
@st.cache_data(ttl=10)
def load_monitoring():
    runs      = query("SELECT id, agent_name, status, started_at, risk_level, approval_required FROM agent_runs ORDER BY started_at DESC")
    tool_calls= query("SELECT tool_name, latency_ms, success, created_at FROM tool_calls ORDER BY created_at DESC")
    approvals = query("SELECT status, risk_level FROM approval_requests")
    return runs, tool_calls, approvals

runs, tool_calls, approvals = load_monitoring()

total     = len(runs)
completed = [r for r in runs if r["status"] == "completed"]
failed    = [r for r in runs if r["status"] == "failed"]
succ_rate = round(len(completed) / total * 100, 1) if total else 0
fail_calls= sum(1 for t in tool_calls if not t["success"])
avg_lat   = round(sum(t["latency_ms"] for t in tool_calls) / len(tool_calls)) if tool_calls else 0
pend      = sum(1 for a in approvals if a["status"] == "pending")
appr      = sum(1 for a in approvals if a["status"] == "approved")
decided   = sum(1 for a in approvals if a["status"] in ("approved", "rejected"))
appr_rate = round(appr / decided * 100, 1) if decided else 0
esc_rate  = round(sum(1 for a in approvals if a["status"] == "escalated") / total * 100, 1) if total else 0

# ── KPIs ──────────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Agent Runs",  total)
c2.metric("Success Rate",      f"{succ_rate}%")
c3.metric("Failed Tool Calls", fail_calls,  delta_color="inverse")
c4.metric("Avg Latency",       f"{avg_lat} ms")

c5, c6, c7, c8 = st.columns(4)
c5.metric("Pending Approvals", pend, delta_color="inverse" if pend else "off")
c6.metric("Approval Rate",     f"{appr_rate}%")
c7.metric("Escalation Rate",   f"{esc_rate}%")
c8.metric("Tool Calls Logged", len(tool_calls))

st.markdown("---")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_runs, tab_tools, tab_evals, tab_gov = st.tabs([
    "📈 Agent Runs", "🔧 Tool Performance", "🧪 Evaluations", "🛡️ Governance"
])

# ── Tab: Agent Runs ───────────────────────────────────────────────────────────
with tab_runs:
    st.subheader("Agent Runs — Last 30 Days")
    df_runs = pd.DataFrame(runs)
    if not df_runs.empty and "started_at" in df_runs.columns:
        df_runs["date"] = pd.to_datetime(df_runs["started_at"].str[:10], errors="coerce")
        daily = df_runs.groupby("date").agg(
            runs      =("id", "count"),
            successes =("status", lambda x: (x == "completed").sum()),
            failures  =("status", lambda x: (x == "failed").sum()),
        ).reset_index()

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=daily["date"], y=daily["runs"], mode="lines+markers",
                                 name="Total Runs", line=dict(color="#2563eb", width=2),
                                 fill="tozeroy", fillcolor="rgba(37,99,235,0.08)"))
        fig.add_trace(go.Scatter(x=daily["date"], y=daily["successes"], mode="lines",
                                 name="Successes", line=dict(color="#16a34a", width=1.5, dash="dot")))
        fig.add_trace(go.Scatter(x=daily["date"], y=daily["failures"], mode="lines",
                                 name="Failures", line=dict(color="#dc2626", width=1.5, dash="dash")))
        fig.update_layout(height=260, margin=dict(l=0,r=0,t=0,b=0),
                          legend=dict(orientation="h", yanchor="bottom", y=1.02),
                          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                          xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.15)"))
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Recent Runs")
        df_recent = df_runs.head(10)[["id","agent_name","status","started_at","risk_level"]].copy()
        df_recent.columns = ["ID","Agent","Status","Started At","Risk"]
        st.dataframe(df_recent, use_container_width=True, hide_index=True)
    else:
        st.info("No agent run data yet.")

# ── Tab: Tool Performance ─────────────────────────────────────────────────────
with tab_tools:
    st.subheader("Tool Latency & Reliability")
    if tool_calls:
        df_tc = pd.DataFrame(tool_calls)
        stats = df_tc.groupby("tool_name").agg(
            avg_ms       =("latency_ms", "mean"),
            calls        =("latency_ms", "count"),
            success_rate =("success", lambda x: round(x.mean()*100, 1)),
        ).reset_index().sort_values("avg_ms")
        stats["avg_ms"] = stats["avg_ms"].round().astype(int)

        fig_lat = px.bar(stats, x="avg_ms", y="tool_name", orientation="h",
                         color="success_rate",
                         color_continuous_scale=["#dc2626","#fbbf24","#16a34a"],
                         range_color=[90,100],
                         labels={"avg_ms":"Avg Latency (ms)","tool_name":"","success_rate":"Success %"},
                         height=380)
        fig_lat.update_layout(margin=dict(l=0,r=0,t=0,b=0),
                               coloraxis_colorbar=dict(title="Success %", thickness=12),
                               plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                               xaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.15)"),
                               yaxis=dict(showgrid=False))
        st.plotly_chart(fig_lat, use_container_width=True)

        st.dataframe(
            stats.rename(columns={"tool_name":"Tool","avg_ms":"Avg ms","calls":"Calls","success_rate":"Success %"}),
            use_container_width=True, hide_index=True,
        )
    else:
        st.info("No tool call data yet.")

# ── Tab: Evaluations ──────────────────────────────────────────────────────────
with tab_evals:
    st.subheader("Evaluation Suite")

    left_ev, right_ev = st.columns([2, 3], gap="large")

    with left_ev:
        st.markdown("**Run Evals**")
        st.caption("Runs all 4 eval cases against the live graph. No LLM required — checks are deterministic.")

        if st.button("🧪 Run All Evals", type="primary", use_container_width=True):
            with st.spinner("Running 4 eval cases against the graph..."):
                results = run_all_evals()
            st.cache_data.clear()

            for r in results:
                icon  = "✅" if r["passed"] else "❌"
                color = "rgba(22,163,74,0.12)" if r["passed"] else "rgba(220,38,38,0.12)"
                tc    = "#16a34a" if r["passed"] else "#dc2626"
                with st.container(border=True):
                    st.markdown(
                        f"{icon} **{r['id']}** — {r['name']} "
                        f"<span style='background:{color};color:{tc};border-radius:4px;"
                        f"padding:1px 8px;font-size:0.75rem;font-weight:700;'>{r['pass_fail']}</span> "
                        f"({r['checks_passed']}/{r['checks_total']} checks)",
                        unsafe_allow_html=True,
                    )
                    if not r["passed"]:
                        for chk in r["check_results"]:
                            if not chk["passed"]:
                                st.caption(f"❌ {chk['description']} → {chk['detail']}")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**CLI runner:**")
        st.code("python -m evals.run_evals --verbose", language="bash")
        st.markdown("**pytest:**")
        st.code("pytest evals/test_agent_flows.py -v", language="bash")

    with right_ev:
        st.markdown("**Eval History & Drift Detection**")

        history = get_eval_history(limit=40)
        if history:
            df_hist = pd.DataFrame(history)
            df_hist["run_at"] = pd.to_datetime(df_hist["run_at"].str[:10], errors="coerce")
            df_hist["pass_rate"] = df_hist["checks_passed"] / df_hist["checks_total"].replace(0, 1) * 100

            # Drift chart — pass rate per eval over time
            fig_drift = px.line(
                df_hist, x="run_at", y="pass_rate", color="eval_name",
                markers=True,
                labels={"run_at": "Date", "pass_rate": "Check Pass Rate %", "eval_name": "Eval"},
                height=260,
                title="Eval Pass Rate Over Time (Drift Detection)",
            )
            fig_drift.update_layout(
                margin=dict(l=0,r=0,t=40,b=0),
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                yaxis=dict(range=[0,105], showgrid=True, gridcolor="rgba(128,128,128,0.15)"),
                xaxis=dict(showgrid=False),
                legend=dict(orientation="h", yanchor="top", y=-0.2),
                title=dict(font=dict(size=13)),
            )
            fig_drift.add_hline(y=100, line_dash="dot", line_color="#16a34a",
                                annotation_text="100% pass", annotation_position="right")
            st.plotly_chart(fig_drift, use_container_width=True)

            # Latest result per eval
            latest = df_hist.sort_values("run_at", ascending=False).drop_duplicates("eval_id")
            for _, row in latest.iterrows():
                pf    = row["pass_fail"]
                color = "rgba(22,163,74,0.12)" if pf == "PASS" else "rgba(220,38,38,0.12)"
                tc    = "#16a34a" if pf == "PASS" else "#dc2626"
                icon  = "✅" if pf == "PASS" else "❌"
                st.markdown(
                    f"{icon} **{row['eval_id']}** — {row['eval_name']} "
                    f"<span style='background:{color};color:{tc};border-radius:4px;"
                    f"padding:1px 8px;font-size:0.75rem;font-weight:700;'>{pf}</span> "
                    f"({int(row['checks_passed'])}/{int(row['checks_total'])}) — {str(row['run_at'])[:10]}",
                    unsafe_allow_html=True,
                )
        else:
            st.info("No eval runs yet. Click 'Run All Evals' to start.")

# ── Tab: Governance ───────────────────────────────────────────────────────────
with tab_gov:
    st.subheader("Approval & Risk Breakdown")
    g1, g2 = st.columns(2)

    with g1:
        apr_counts = {
            "Approved":  sum(1 for a in approvals if a["status"] == "approved"),
            "Rejected":  sum(1 for a in approvals if a["status"] == "rejected"),
            "Escalated": sum(1 for a in approvals if a["status"] == "escalated"),
            "Pending":   sum(1 for a in approvals if a["status"] == "pending"),
        }
        fig_donut = go.Figure(go.Pie(
            labels=list(apr_counts.keys()), values=list(apr_counts.values()),
            hole=0.55, marker_colors=["#16a34a","#dc2626","#7c3aed","#d97706"],
            textinfo="label+percent",
        ))
        fig_donut.update_layout(height=260, margin=dict(l=0,r=0,t=0,b=0),
                                 showlegend=False, paper_bgcolor="rgba(0,0,0,0)",
                                 title=dict(text="Approval Queue Status", x=0.5, font=dict(size=13)))
        st.plotly_chart(fig_donut, use_container_width=True)

    with g2:
        risk_counts = {"High":0,"Medium":0,"Low":0}
        for a in approvals:
            k = a["risk_level"].capitalize()
            if k in risk_counts:
                risk_counts[k] += 1
        fig_risk = go.Figure(go.Bar(
            x=list(risk_counts.keys()), y=list(risk_counts.values()),
            marker_color=["#dc2626","#d97706","#16a34a"],
            text=list(risk_counts.values()), textposition="outside",
        ))
        fig_risk.update_layout(height=260, margin=dict(l=0,r=0,t=30,b=0),
                                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                                yaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.15)"),
                                xaxis=dict(showgrid=False),
                                title=dict(text="Requests by Risk Level", x=0.5, font=dict(size=13)))
        st.plotly_chart(fig_risk, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Refresh Metrics", use_container_width=False):
        st.cache_data.clear()
        st.rerun()

st.markdown("---")
st.caption("All metrics sourced live from agent_runs, tool_calls, approval_requests, and eval_runs tables.")
