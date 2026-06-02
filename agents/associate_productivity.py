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
                "You are a corporate workflow advisor at a national homebuilder.\n\n"
                "An associate needs guidance on a process. Answer using the policy provided.\n\n"
                "EXAMPLE OF A GOOD ANSWER:\n"
                "Question: How do I get a vendor contract approved?\n"
                "Answer: Per the Vendor Onboarding Policy, contracts under $25,000 require "
                "Division Manager approval, while contracts above $25,000 require VP Procurement "
                "sign-off. Submit the vendor's insurance certificate and risk assessment through "
                "the procurement portal before requesting approval — contracts with expired "
                "insurance cannot proceed regardless of value.\n\n"
                "NOW ANSWER THE ACTUAL QUESTION:\n"
                "- 2-3 sentences maximum\n"
                "- Cite the policy name (e.g. 'Per the [Policy Name]...')\n"
                "- State the exact approval threshold and who signs off\n"
                "- If the policy does not fully address the question, end with: "
                "'The [policy name] does not cover [specific gap] — "
                "contact [business_function] for further guidance.'\n"
                "- Professional tone. No bullet points."
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
