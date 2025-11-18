from .agents import IntentRouter, RAGFAQAgent, TroubleshooterAgent, EscalationSupervisor, TicketingAgent
from .agents import llm_model
from typing import Dict, Any, List

router = IntentRouter()
faq_agent = RAGFAQAgent(llm_model)
troubleshooter = TroubleshooterAgent()
supervisor = EscalationSupervisor()
ticketing = TicketingAgent()

async def run_workflow(messages: list):


    intent, _ = await router.route(messages)

    if "faq" in intent:
        res = await faq_agent.answer(messages)
        return {"answer": res["answer"], "sources": res.get("sources", [])}

    if "troubleshooting" in intent:
        cont = await troubleshooter.continue_convo(messages)
        return {"answer": cont["next_question"] if not cont.get("done") else cont["answer"]}

    if "escalation" in intent:
        res = await supervisor.evaluate(messages)
        return {"answer": f"Routing to {res} support regarding your query."}

    if "ticketing" in intent:
        return {}

    res = await supervisor.evaluate(messages)
    return {"answer": res["answer"], "sources": res.get("sources", [])}
