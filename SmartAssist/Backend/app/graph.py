from .agents import IntentRouter, RAGFAQAgent, TroubleshooterAgent, EscalationSupervisor, TicketingAgent
from .state import state
from .logger import logger

router = IntentRouter()
faq_agent = RAGFAQAgent()
troubleshooter = TroubleshooterAgent()
supervisor = EscalationSupervisor([])
ticketing = TicketingAgent([])

async def run_workflow(messages: list):
    logger.info("Running workflow with %d messages", len(messages))
    try:
        intent = await router.route(messages)
        logger.info("Determined intent: %s", intent.get("answer"))

        if "faq" in intent.get("answer", ""):
            res = faq_agent.answer(messages)
            logger.info("FAQ Agent response generated")
            return {"answer": res["answer"]}

        if "troubleshoot" in intent.get("answer", ""):
            res = troubleshooter.answer(messages)
            logger.info("Troubleshooter Agent response generated")
            return {"answer": res["answer"]}

        if "escalation" in intent.get("answer", ""):
            state["is_escalation"] = True
            res = supervisor.answer(messages)
            logger.info("Escalation Supervisor response generated")
            return {"answer": res["answer"]}

        # Fallback escalation
        state["is_escalation"] = True
        res = supervisor.answer(messages)
        logger.info("Fallback Escalation Supervisor response generated")
        return {"answer": res["answer"]}

    except Exception as e:
        logger.error("Error in run_workflow: %s", str(e))
        state["is_escalation"] = True
        return {"answer": "An error occurred. Escalating to human agent."}
