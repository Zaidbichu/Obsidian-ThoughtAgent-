import os
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI


def get_llm(openai_api_key: str = "", temperature: float = 0.2):
    """
    Dynamically returns ChatOpenAI if a key is provided,
    otherwise returns local ChatOllama.
    """
    key_str = (openai_api_key or "").strip()

    if key_str:
        # Assign key to environment to ensure inner client handles it
        os.environ["OPENAI_API_KEY"] = key_str
        return ChatOpenAI(
            model="gpt-4o-mini",
            api_key=key_str,
            temperature=temperature
        )
    else:
        # Assign dummy key to environment to prevent ChatOpenAI/LangChain 
        # validation checks from throwing missing credentials errors
        os.environ["OPENAI_API_KEY"] = "ollama-local-dummy-key"
        
        return ChatOllama(
            model="gemma3:4b",  # Or qwen3:8b
            temperature=temperature,
            base_url="http://localhost:11434"
        )
