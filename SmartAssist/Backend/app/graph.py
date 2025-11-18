from .agents import IntentRouter, RAGFAQAgent, TroubleshooterAgent, EscalationSupervisor, TicketingAgent
from .main import state
router = IntentRouter()
faq_agent = RAGFAQAgent()
troubleshooter = TroubleshooterAgent()
supervisor = EscalationSupervisor()
ticketing = TicketingAgent()

async def run_workflow(messages: list):
    intent = await router.route(messages)

    if "faq" in intent:
        res = await faq_agent.answer(messages)
        return {"answer": res["answer"]}

    if "troubleshooting" in intent:
        res = await troubleshooter.answer(messages)
        return {"answer": res["answer"]}

    if "escalation" in intent:
        state["is_escalation"] = True
        res = await supervisor.answer(messages)
        return {"answer": res["answer"]}

    state["is_escalation"] = True
    res = await supervisor.answer(messages)
    return {"answer": res["answer"]}
