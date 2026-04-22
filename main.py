from app.graph.builder import build_graph

app = build_graph()

def run_agent(query):
    return app.invoke({"input": query})