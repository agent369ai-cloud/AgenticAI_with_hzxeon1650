import os
import uuid
from typing import TypedDict, List

import streamlit as st
from dotenv import load_dotenv

from langchain_ollama import OllamaLLM
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import tool

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# -------------------------
# ENV
# -------------------------
load_dotenv()
assert os.getenv("LANGCHAIN_API_KEY"), "Missing LANGCHAIN_API_KEY"

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "agent-langgraph"

# -------------------------
# Session
# -------------------------
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# -------------------------
# Tools
# -------------------------
@tool
def calculator(expr: str) -> str:
    """Evaluate a math expression like '12*7'."""
    try:
        return str(eval(expr))
    except Exception:
        return "Invalid expression"

# -------------------------
# State
# -------------------------
class AgentState(TypedDict):
    messages: List
    tool_output: str

# -------------------------
# LLM
# -------------------------
llm = OllamaLLM(model="llama3", timeout=60)

# -------------------------
# Nodes
# -------------------------
def plan(state: AgentState):
    """LLM decides what to do."""
    last = state["messages"][-1].content

    prompt = f"""
You are an agent. Decide:
- If math → use tool: calculator
- Else → answer directly

User: {last}
Respond ONLY with:
TOOL: <expression>
OR
FINAL: <answer>
"""
    out = llm.invoke(prompt)
    return {"messages": state["messages"] + [AIMessage(content=out)]}


def route(state: AgentState):
    """Route based on LLM decision."""
    decision = state["messages"][-1].content
    if decision.startswith("TOOL:"):
        return "tool"
    return "final"


def tool_exec(state: AgentState):
    decision = state["messages"][-1].content
    expr = decision.replace("TOOL:", "").strip()
    result = calculator.invoke(expr)

    return {
        "tool_output": result,
        "messages": state["messages"] + [
            AIMessage(content=f"Tool result: {result}")
        ],
    }


def respond(state: AgentState):
    last_user = state["messages"][0].content
    tool_out = state.get("tool_output", "")

    prompt = f"""
User: {last_user}
Tool result: {tool_out}

Provide final answer.
"""
    out = llm.invoke(prompt)

    return {"messages": state["messages"] + [AIMessage(content=out)]}


# -------------------------
# Graph
# -------------------------
builder = StateGraph(AgentState)

builder.add_node("plan", plan)
builder.add_node("tool", tool_exec)
builder.add_node("respond", respond)

builder.set_entry_point("plan")

builder.add_conditional_edges(
    "plan",
    route,
    {
        "tool": "tool",
        "final": "respond",
    },
)

builder.add_edge("tool", "respond")
builder.add_edge("respond", END)

memory = MemorySaver()

graph = builder.compile(checkpointer=memory)

# -------------------------
# UI
# -------------------------
st.title("Raja-Demo + LangGraph Agent + Ollama + LangSmith")

query = st.text_input("Ask something")

if query:
    state = {
        "messages": [HumanMessage(content=query)],
        "tool_output": "",
    }

    result = graph.invoke(
        state,
        config={
            "configurable": {"thread_id": st.session_state.session_id},
            "metadata": {"app": "langgraph-agent"},
            "tags": ["agent", "ollama", "langgraph"],
        },
    )

    st.write(result["messages"][-1].content)



    #pip install -U langgraph langchain-core langchain-ollama langsmith streamlit python-dotenv