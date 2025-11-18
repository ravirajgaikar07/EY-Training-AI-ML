from typing import TypedDict, Optional, Any, Dict, List, Annotated
import operator
import asyncio
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, SystemMessage, AnyMessage
import agents as agents_module


# ==========================
# 1. State Definition
# ==========================
class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    convo_history: Annotated[List[Dict[str, Any]], operator.add]
    intent: Optional[str]
    latest_agent_output: Optional[Dict[str, Any]]


def ensure_state(state: Optional[Dict]) -> AgentState:
    if state is None:
        state = {}
    return AgentState(
        messages=state.get("messages", []),
        convo_history=state.get("convo_history", []),
        intent=state.get("intent"),
        latest_agent_output=state.get("latest_agent_output")
    )


# ==========================
# 2. Nodes
# ==========================
def router_node(state: Dict) -> Dict:
    st = ensure_state(state)
    last_human = next((m for m in reversed(st["messages"]) if isinstance(m, HumanMessage)), None)
    if not last_human:
        return {"latest_agent_output": {"error": "No human message found"}}

    router = agents_module.IntentRouter()
    intent, score = asyncio.get_event_loop().run_until_complete(router.route(last_human.content))

    return {
        "messages": [SystemMessage(content=f"Intent: {intent} && Confidence: {score}")],
        "convo_history": [{"role": "agent", "text": f"Intent: {intent} && Confidence: {score}"}],
        "intent": intent,
        "latest_agent_output": {"router_score": score}
    }


def faq_node(state: Dict) -> Dict:
    st = ensure_state(state)
    last_human = next((m for m in reversed(st["messages"]) if isinstance(m, HumanMessage)), None)

    rag = agents_module.RAGFAQAgent(agents_module.llm_model)
    res = asyncio.get_event_loop().run_until_complete(rag.answer(last_human.content)) \
        if asyncio.iscoroutinefunction(rag.answer) else rag.answer(last_human.content)

    return {
        "messages": [SystemMessage(content=f"[faq] {res.get('answer', '')}")],
        "convo_history": [{"role": "agent", "text": res.get("answer", "")}]
    }


def troubleshooter_node(state: Dict) -> Dict:
    st = ensure_state(state)
    ts = agents_module.TroubleshooterAgent()

    last_human = next((m for m in reversed(st["messages"]) if isinstance(m, HumanMessage)), None)
    step = ts.step("", last_human.content)  # Minimal: skipping convo_id

    return {
        "messages": [SystemMessage(content=f"[troubleshooter] {step.get('question', '')}")],
        "convo_history": [{"role": "agent", "text": step.get("question", "")}]
    }


def supervisor_node(state: Dict) -> Dict:
    st = ensure_state(state)
    sup = agents_module.EscalationSupervisor()
    eval_result = sup.evaluate(st["convo_history"], st.get("latest_agent_output"))

    return {
        "messages": [SystemMessage(content=f"[supervisor] escalate={eval_result.get('escalate', False)}")],
        "convo_history": [{"role": "system", "text": f"[supervisor] escalate={eval_result.get('escalate', False)}"}]
    }


def ticket_node(state: Dict) -> Dict:
    st = ensure_state(state)
    # Skip if no ticketing needed
    return {}


def end_node(state: Dict) -> Dict:
    st = ensure_state(state)
    latest = st.get("latest_agent_output") or {}
    reply = latest.get("answer") or latest.get("question") or "No response."

    return {
        "messages": [SystemMessage(content=f"[final] {reply}")],
        "convo_history": [{"role": "agent", "text": reply}]
    }


# ==========================
# 3. Graph Setup
# ==========================
graph = StateGraph(AgentState)

graph.add_node("router", router_node)
graph.add_node("faq", faq_node)
graph.add_node("troubleshooter", troubleshooter_node)
graph.add_node("supervisor", supervisor_node)
graph.add_node("ticket", ticket_node)
graph.add_node("end", end_node)


def route_after_router(state: AgentState) -> str:
    intent = state.get("intent")
    if intent == "faq":
        return "faq"
    if intent == "troubleshooting":
        return "troubleshooter"
    return "faq"


graph.add_edge(START, "router")
graph.add_conditional_edges("router", route_after_router, ["faq", "troubleshooter"])
graph.add_edge("faq", "supervisor")
graph.add_edge("troubleshooter", "supervisor")
graph.add_edge("supervisor", "end")
graph.add_edge("ticket", "end")  # minimal
graph.add_edge("supervisor", "end")

agent = graph.compile()
