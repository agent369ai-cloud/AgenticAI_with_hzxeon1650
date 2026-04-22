import os
from dotenv import load_dotenv
from typing import TypedDict, List

# Load env variables
load_dotenv()

# ---------------------------
# LangChain / LangGraph imports
# ---------------------------
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_community.llms import Ollama

llm = Ollama(model="llama3")
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition

# ---------------------------
# 1. Define State
# ---------------------------
class AgentState(TypedDict):
    messages: List[BaseMessage]
# ---------------------------
# 2. Define Tool (SAFE-ish version)
# ---------------------------
@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression like '2+3*5'."""
    try:
        # basic validation (VERY IMPORTANT)

        allowed_chars = "0123456789+-*/(). "
        if not all(c in allowed_chars for c in expression):
            return "Invalid or unsafe expression"

        return str(eval(expression))
    except Exception:
        return "Invalid expression"

llm_with_tools = llm.bind_tools([calculator])
# ---------------------------
# 4. System Prompt (IMPORTANT)
# ---------------------------
SYSTEM_PROMPT = """
You are a strict math agent.

Rules:
- Always use the calculator tool for ANY math
- Never calculate yourself
- Pass expressions like '2+3*5'
"""

# ---------------------------
# 5. LLM Node
# ---------------------------
def llm_node(state: AgentState):
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

# ---------------------------
# 6. Build Graph
# ---------------------------
builder = StateGraph(AgentState)

builder.add_node("llm", llm_node)
builder.add_node("tools", ToolNode([calculator]))

builder.set_entry_point("llm")

builder.add_conditional_edges(
    "llm",
    tools_condition,
    {
        "tools": "tools",
        "__end__": END
    }
)

builder.add_edge("tools", "llm")

graph = builder.compile()

# ---------------------------
# 7. Run Agent
# ---------------------------
if __name__ == "__main__":
    while True:
        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit"]:
            break

        result = graph.invoke({
            "messages": [HumanMessage(content=user_input)]
        })

        print("\nAgent:", result["messages"][-1].content, "\n")