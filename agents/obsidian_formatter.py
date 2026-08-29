from datetime import datetime
from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from utils.model_refactory import get_llm


def run_obsidian(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Formats the synthesis into an Obsidian Markdown document with WikiLinks and references.
    """
    topic = state.get("topic", "")
    synthesis = state.get("synthesis", "")
    search_results = state.get("search_results", [])
    openai_key = state.get("openai_api_key", "")
    temp = state.get("temperature", 0.2)

    llm = get_llm(openai_api_key=openai_key, temperature=temp)

    reference_block = "\n".join([
        f"- [{item.get('title')}]({item.get('url')})"
        for item in search_results if item.get("url")
    ])

    prompt_template = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are an Obsidian Knowledge Management Expert. Format research syntheses into standard "
            "Obsidian Markdown files with YAML frontmatter and [[WikiLinks]]."
        ),
        (
            "human",
            "Topic: {topic}\n"
            "Date: {date}\n\n"
            "Rules:\n"
            "1. Output exact YAML frontmatter at top: title, date, tags (e.g. [research, ai]), status.\n"
            "2. Wrap important technical concepts in double brackets (e.g., [[Vector Databases]]).\n"
            "3. Use structured markdown headers (##, ###).\n"
            "4. Append a '## References' section at the bottom.\n\n"
            "Synthesis:\n{synthesis}\n\n"
            "References:\n{references}"
        )
    ])

    current_date = datetime.now().strftime("%Y-%m-%d")

    chain = prompt_template | llm | StrOutputParser()
    response = chain.invoke({
        "topic": topic,
        "date": current_date,
        "synthesis": synthesis,
        "references": reference_block if reference_block else "- Web Research Session"
    })

    return {"obsidian_md": response}