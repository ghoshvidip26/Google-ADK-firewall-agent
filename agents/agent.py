from langgraph.graph import StateGraph,START,END
from typing import TypedDict
from langchain_ollama import ChatOllama
from agents.orchaestratorAgent import orchaestrate
from agents.userQueryAgent import takeQuery
from agents.queryAnalysisAgent import analyze

class AgentState(TypedDict):
    query: str
    analysis: str
    decision: str

graph = StateGraph(AgentState)
graph.add_node("takeQuery", takeQuery)
graph.add_node("analyze", analyze)
graph.add_node("orchaestrate", orchaestrate)

graph.add_edge(START,'takeQuery')
graph.add_edge('takeQuery','analyze')
graph.add_edge('analyze','orchaestrate')
graph.add_edge('orchaestrate',END)

workflow = graph.compile()

if __name__ == "__main__":
    response = workflow.invoke({"query":"delete all files"})
    print(response)