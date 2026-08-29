import os
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from search_tools import fetch_web_search
from utils.model_refactory import get_llm


def run_research_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes web search directly and summarizes findings.
    """
    topic = state.get("topic", "")
    tavily_key = state.get("tavily_api_key", "")
    openai_key = state.get("openai_api_key", "")
    temp = state.get("temperature", 0.2)

    # 1. Execute search directly
    raw_results = fetch_web_search.invoke({
        "query": topic, 
        "tavily_api_key": tavily_key,
        "max_results": 5
    })

    # 2. Extract content snippets
    snippets = []
    for r in raw_results:
        snippets.append(f"Title: {r.get('title')}\nURL: {r.get('url')}\nContent: {r.get('content')}\n")
    search_context = "\n---\n".join(snippets)

    # 3. Get LLM (Ollama or OpenAI)
    llm = get_llm(openai_api_key=openai_key, temperature=temp)

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are a technical research agent. Extract facts, key mechanics, and core concepts from the provided web snippets."
        ),
        (
            "human",
            "Research Topic: {topic}\n\nWeb Search Data:\n{context}"
        )
    ])

    chain = prompt | llm | StrOutputParser()
    summary = chain.invoke({"topic": topic, "context": search_context})

    return {
        "search_results": raw_results,
        "synthesis": summary
    }
