from typing import Dict, Any
from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from utils.model_factory import get_llm

def run_obsidian(state: Dict[str, Any], config: Dict[str, Any] = None) -> Dict[str, Any]:
    config = config or {}
    
    # 1. Read input state (outputted by synthesizer_agent)
    query = state.get("query") or state.get("topic", "")
    synthesized_text = state.get("synthesized_text", "")
    
    # 2. Instantiate LLM dynamically using runtime config
    llm = get_llm(
        provider=config.get("provider", "ollama"),
        model_name=config.get("model_name"),
        api_key=config.get("api_key")
    )
    
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # 3. Prompt setup for Obsidian Vault markdown formatting
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are an expert Obsidian Knowledge Graph Architect. Convert the input analysis into a fully "
            "formatted Obsidian Markdown note.\n\n"
            "Requirements:\n"
            "1. Must start with YAML Frontmatter containing title, date ({date}), and relevant tags.\n"
            "2. Use clean markdown headings (##, ###).\n"
            "3. Enclose important core technical terms and topics inside [[WikiLinks]] so they link to other vault notes.\n"
            "4. Do NOT wrap your whole response in a python code block; output raw markdown content."
        ),
        (
            "human",
            "Topic: {topic}\n\nSynthesized Content:\n{content}"
        )
    ])
    
    chain = prompt | llm | StrOutputParser()
    final_output = chain.invoke({
        "topic": query,
        "content": synthesized_text,
        "date": current_date
    })
    
    # 4. Return final output state key
    return {
        "final_output": final_output
    }
