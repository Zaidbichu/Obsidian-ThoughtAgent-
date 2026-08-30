import os
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from search_tools import fetch_web_search
from utils.model_factory import get_llm

def run_research_agent(state: dict, config: dict = None) -> dict:
    config = config or {}
    
    # 1. Extract inputs correctly
    # Use 'query' (matches app.py state key) and fallback to 'topic'
    query = state.get("query") or state.get("topic", "")
    
    # Extract keys and parameters from runtime `config` passed by app.py
    tavily_key = config.get("tavily_key", "")
    provider = config.get("provider", "ollama")
    model_name = config.get("model_name")
    api_key = config.get("api_key")

    # 2. Dynamically initialize LLM using runtime config
    llm = get_llm(
        provider=provider,
        model_name=model_name,
        api_key=api_key
    )

    # 3. Execute search tool
    raw_results = fetch_web_search.invoke({
        "query": query, 
        "tavily_api_key": tavily_key,
        "max_results": 5
    })

    # 4. Extract content snippets safely
    snippets = []
    if isinstance(raw_results, list):
        for r in raw_results:
            if isinstance(r, dict):
                snippets.append(f"Title: {r.get('title', 'N/A')}\nURL: {r.get('url', 'N/A')}\nContent: {r.get('content', '')}\n")
    
    search_context = "\n---\n".join(snippets) if snippets else "No search results found."

    # 5. Build prompt and execute chain
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
    summary = chain.invoke({"topic": query, "context": search_context})

    # 6. Return standard keys expected by GraphState & synthesizer agent
    return {
        "search_results": raw_results,
        "research_data": summary
    }
