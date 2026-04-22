from langgraph.graph import StateGraph
from app.graph.nodes import llm_node, tool_node
from app.graph.router import route

def build_graph():
    graph = StateGraph(dict)

    graph.add_node("llm", llm_node)
    graph.add_node("tool", tool_node)

    graph.set_entry_point("llm")

    graph.add_conditional_edges(
        "llm",
        route,
        {
            "tool": "tool",
            "end": "__end__"
        }
    )

    graph.add_edge("tool", "__end__")

    return graph.compile()