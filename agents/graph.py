"""
HomeBuilder Workforce AI — LangGraph Supervisor Graph

Graph structure (linear pipeline, each specialist skips itself if not selected):
  classify → community_performance → construction_delay → finance_incentive
           → marketing_campaign → vendor_approval → associate_productivity
           → critic_validate → generate_response → finalize → END
"""
from langgraph.graph import StateGraph, END
from agents.state import AgentState


def build_graph():
    from agents.executive           import classify_node, generate_response_node, finalize_node
    from agents.community_performance import run as community_run
    from agents.construction_delay  import run as delay_run
    from agents.finance_incentive   import run as finance_run
    from agents.marketing_campaign  import run as marketing_run
    from agents.vendor_approval     import run as vendor_run
    from agents.associate_productivity import run as associate_run
    from agents.critic              import validate as critic_run

    wf = StateGraph(AgentState)

    wf.add_node("classify",                classify_node)
    wf.add_node("community_performance",   community_run)
    wf.add_node("construction_delay",      delay_run)
    wf.add_node("finance_incentive",       finance_run)
    wf.add_node("marketing_campaign",      marketing_run)
    wf.add_node("vendor_approval",         vendor_run)
    wf.add_node("associate_productivity",  associate_run)
    wf.add_node("critic_validate",         critic_run)
    wf.add_node("generate_response",       generate_response_node)
    wf.add_node("finalize",                finalize_node)

    wf.set_entry_point("classify")
    wf.add_edge("classify",               "community_performance")
    wf.add_edge("community_performance",  "construction_delay")
    wf.add_edge("construction_delay",     "finance_incentive")
    wf.add_edge("finance_incentive",      "marketing_campaign")
    wf.add_edge("marketing_campaign",     "vendor_approval")
    wf.add_edge("vendor_approval",        "associate_productivity")
    wf.add_edge("associate_productivity", "critic_validate")
    wf.add_edge("critic_validate",        "generate_response")
    wf.add_edge("generate_response",      "finalize")
    wf.add_edge("finalize",               END)

    return wf.compile()
