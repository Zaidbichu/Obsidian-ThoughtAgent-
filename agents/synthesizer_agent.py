from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from utils.model_factory import get_llm

def run_synthesizer_agent(state: Dict[str, Any], config: Dict[str, Any] = None) -> Dict[str, Any]:
    config = config or {}
    
    # 1. Read input state (outputted by researcher_agent)
    query = state.get("query") or state.get("topic", "")
    research_data = state.get("research_data", "")
    
    # 2. Instantiate LLM dynamically using runtime config
    llm = get_llm(
        provider=config.get("provider", "ollama"),
        model_name=config.get("model_name"),
        api_key=config.get("api_key")
    )
    
    # 3. Prompt setup
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are a Senior Technical Analyst. Your task is to take raw research notes and synthesize "
            "them into a clear, structured analytical report. Organize by key concepts, mechanisms, and findings."
        ),
        (
            "human",
            "Topic: {topic}\n\nRaw Research Notes:\n{research_data}"
        )
    ])
    
    chain = prompt | llm | StrOutputParser()
    synthesized_text = chain.invoke({
        "topic": query,
        "research_data": research_data
    })
    
    # 4. Return state key expected by Obsidian Formatter node
    return {
        "synthesized_text": synthesized_text
    }
