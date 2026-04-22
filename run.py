from app.main import run_agent

while True:
    query = input(">> ")
    if query == "exit":
        break

    response = run_agent(query)
    print(response["response"])

    def route(state):
    text = state["input"]

    if any(op in text for op in "+-*/"):
        return "tool"

    return "end"