from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import logging
from datetime import date
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
from langchain.tools import tool
from langchain.messages import AnyMessage, SystemMessage, ToolMessage
from typing_extensions import TypedDict, Annotated
import operator
from typing import Literal
from langgraph.graph import StateGraph, START, END
from langchain.chat_models import init_chat_model
import time

# -------------------------------------------------------------------------
# ENV + LOGGING
# -------------------------------------------------------------------------
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in .env file")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log", mode="a", encoding="utf-8"),  # File log
        logging.StreamHandler()  # Console log
    ]
)
logger = logging.getLogger(__name__)

# -------------------------------------------------------------------------
# APP INITIALIZATION
# -------------------------------------------------------------------------
app = FastAPI()

# Middleware for logging and timing
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    logger.info(f"Incoming request: {request.method} {request.url.path}")
    try:
        response = await call_next(request)
    except Exception as e:
        logger.exception(f"Unhandled error: {e}")
        return JSONResponse(status_code=500, content={"error": "Internal server error"})
    process_time = (time.time() - start_time) * 1000
    logger.info(f"Completed {request.method} {request.url.path} in {process_time:.2f}ms")
    return response

# Global error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Global error: {exc}")
    return JSONResponse(status_code=500, content={"error": str(exc)})

# -------------------------------------------------------------------------
# LLM + TOOLS
# -------------------------------------------------------------------------
llm = init_chat_model(
    model="gemini-2.5-flash",
    temperature=0.7,
    model_provider="google_genai"
)

@tool
def math_operations(a: float, b: float) -> float:
    """Add `a` and `b`."""
    return a + b

@tool
def current_date() -> str:
    """Return today's date."""
    return date.today().strftime("%Y-%m-%d")

@tool
def reverse_word(word: str) -> str:
    """Reverse the given word."""
    return word[::-1]

tools = [math_operations, current_date, reverse_word]
tools_by_name = {tool.name: tool for tool in tools}
llm_with_tools = llm.bind_tools(tools)

# -------------------------------------------------------------------------
# LANGGRAPH STATE + NODES
# -------------------------------------------------------------------------
class MessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]

def llm_call(state: dict):
    messages = [SystemMessage(content="You are a helpful assistant.")] + state["messages"]
    result = llm_with_tools.invoke(messages)
    return {"messages": [result]}

def tool_node(state: dict):
    results = []
    for call in state["messages"][-1].tool_calls:
        tool = tools_by_name[call["name"]]
        observation = tool.invoke(call["args"])
        results.append(ToolMessage(content=observation, tool_call_id=call["id"]))
    return {"messages": results}

def should_continue(state: MessagesState) -> Literal["tool_node", END]:
    return "tool_node" if state["messages"][-1].tool_calls else END

# -------------------------------------------------------------------------
# BUILD WORKFLOW
# -------------------------------------------------------------------------
agent_builder = StateGraph(MessagesState)
agent_builder.add_node("llm_call", llm_call)
agent_builder.add_node("tool_node", tool_node)
agent_builder.add_edge(START, "llm_call")
agent_builder.add_conditional_edges("llm_call", should_continue, ["tool_node", END])
agent_builder.add_edge("tool_node", "llm_call")
agent = agent_builder.compile()

# -------------------------------------------------------------------------
# FASTAPI ENDPOINT
# -------------------------------------------------------------------------
class QueryRequest(BaseModel):
    question: str

@app.post("/query")
def handle_query(request: QueryRequest):
    logger.info(f"Processing query: {request.question}")
    messages = [HumanMessage(content=request.question)]
    messages = agent.invoke({"messages": messages})
    return {"response": messages["messages"][-1].content}
