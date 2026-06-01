from agents.state import AgentState
from tools.policy_tools import get_policy_workflow
from services.llm import chat, has_llm

AGENT_NAME = "Associate Productivity Agent"


def run(state: AgentState) -> dict:
    if AGENT_NAME not in state.get("selected_agents", []):
        return {}

    run_id = state.get("run_id")
    prompt = state["user_prompt"]

    # RAG-enhanced policy retrieval
    policy_data  = get_policy_workflow(business_process=prompt, agent_name=AGENT_NAME, run_id=run_id)
    tools_called = ["get_policy_workflow"]

    # Surface RAG retrieval info for transparency
    retrieval_mode = policy_data.get("retrieval", "sql")
    rag_matches    = policy_data.get("rag_matches", [])

    policies = policy_data.get("policies", [])
    if not policies:
        finding = "No matching policy found via semantic or keyword search. Recommend contacting the relevant department."
        return {
            "tool_results": {**state.get("tool_results", {}), "policy": policy_data},
            "agent_outputs": {
                **state.get("agent_outputs", {}),
                AGENT_NAME: {"icon": "👤", "finding": finding, "tools_called": tools_called},
            },
        }

    pol        = policies[0]
    steps      = pol.get("steps", [])
    threshold  = pol.get("approval_threshold", 0)
    escalation = pol.get("escalation_rule", "")

    # RAG context note
    rag_note = ""
    if retrieval_mode == "rag+sql" and rag_matches:
        top = rag_matches[0]
        rag_note = f" (RAG relevance: {top['relevance']:.2f})"

    # LLM for personalized answer
    if has_llm() and steps:
        steps_text = "\n".join(f"{i+1}. {s}" for i, s in enumerate(steps))
        llm_finding = chat(
            system=(
                "You are a corporate workflow advisor at a national homebuilder. "
                "Answer the associate's question directly and concisely using the policy steps. "
                "Highlight key approval thresholds and who needs to sign off. "
                "One paragraph, professional tone, no bullet points."
            ),
            user=(
                f"Associate question: {prompt}\n\n"
                f"Policy: {pol['title']} ({pol['business_function']})\n"
                f"Steps:\n{steps_text}\n"
                f"Approval threshold: ${threshold:,.0f}\n"
                f"Escalation rule: {escalation}"
            ),
        )
    else:
        llm_finding = None

    if llm_finding:
        finding = llm_finding + rag_note
    else:
        finding = (
            f"Retrieved **{pol['title']}** ({pol['business_function']}){rag_note}. "
            f"{len(steps)}-step workflow. "
            f"Approval required above ${threshold:,.0f}. "
            f"Escalation: {escalation}."
        )

    return {
        "tool_results": {**state.get("tool_results", {}), "policy": policy_data},
        "agent_outputs": {
            **state.get("agent_outputs", {}),
            AGENT_NAME: {
                "icon":          "👤",
                "finding":       finding,
                "tools_called":  tools_called,
                "policy_steps":  steps,
                "policy_title":  pol["title"],
                "threshold":     threshold,
                "escalation":    escalation,
                "retrieval_mode": retrieval_mode,
                "rag_matches":   rag_matches,
            },
        },
    }
