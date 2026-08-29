from typing import TypedDict, List, Dict, Any
from langgraph.graph import START, END, StateGraph
from agents.researcher_agent import run_research_agent
from agents.synthesizer_agent import run_synthesizer_agent
from agents.obsidian_formatter import run_obsidian


class AgentState(TypedDict):
    topic: str
    openai_api_key: str
    tavily_api_key: str
    temperature: float
    search_results: List[Dict[str, Any]]
    synthesis: str
    obsidian_md: str


def build_research_graph():
    builder = StateGraph(AgentState)

    builder.add_node("researcher", run_research_agent)
    builder.add_node("synthesis", run_synthesizer_agent)
    builder.add_node("obsidian", run_obsidian)

    builder.add_edge(START, "researcher")
    builder.add_edge("researcher", "synthesis")
    builder.add_edge("synthesis", "obsidian")
    builder.add_edge("obsidian", END)

    return builder.compile()
