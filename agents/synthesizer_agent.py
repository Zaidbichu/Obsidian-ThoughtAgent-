from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from utils.model_refactory import get_llm


def run_synthesizer_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Synthesizes raw data into an objective technical overview.
    """
    topic = state.get("topic", "")
    synthesis_input = state.get("synthesis", "")
    openai_key = state.get("openai_api_key", "")
    temp = state.get("temperature", 0.2)

    llm = get_llm(openai_api_key=openai_key, temperature=temp)

    prompt_template = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are an expert technical research analyst. Synthesize raw research data into a clear, "
            "well-structured analysis highlighting core mechanics, advantages, and drawbacks."
        ),
        (
            "human",
            "Research Topic: {topic}\n\nRaw Findings:\n{synthesis_input}"
        )
    ])

    chain = prompt_template | llm | StrOutputParser()
    response = chain.invoke({'topic': topic, "synthesis_input": synthesis_input})

    return {'synthesis': response}