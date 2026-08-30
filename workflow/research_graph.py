# workflow/research_graph.py
from typing import TypedDict, Dict, Any
from langgraph.graph import START, END, StateGraph
from agents.researcher_agent import run_research_agent
from agents.synthesizer_agent import run_synthesizer_agent
from agents.obsidian_formatter import run_obsidian

class GraphState(TypedDict):
    query: str
    config: Dict[str, Any]  # Stores UI provider selection & API keys
    research_data: str
    synthesized_text: str
    final_output: str

def build_research_graph():
    workflow = StateGraph(GraphState)
    
    # 1. Nodes directly mapping to your original layout
    workflow.add_node("researcher", lambda state: run_research_agent(state, config=state.get("config")))
    workflow.add_node("synthesizer", lambda state: run_synthesizer_agent(state, config=state.get("config")))
    workflow.add_node("formatter", lambda state: run_obsidian(state, config=state.get("config")))

    # 2. Sequential edges
    workflow.add_edge(START, "researcher")
    workflow.add_edge("researcher", "synthesizer")
    workflow.add_edge("synthesizer", "formatter")
    workflow.add_edge("formatter", END)

    return workflow.compile()
