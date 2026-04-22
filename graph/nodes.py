from app.llm.ollama_client import get_llm
from app.tools.calculator import calculate
from app.utils.parser import extract_expression

llm = get_llm()

def llm_node(state):
    return {"response": llm.invoke(state["input"])}

def tool_node(state):
    expr = extract_expression(state["input"])
    result = calculate(expr)
    return {"response": f"Result: {result}"}