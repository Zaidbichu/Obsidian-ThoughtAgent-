import os
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama

def get_llm(
    provider: str = "ollama",
    model_name: Optional[str] = None,
    api_key: Optional[str] = None
):
    """
    Instantiates and returns the configured LLM instance.
    """
    provider = provider.lower()
    
    if provider == "openai":
        # Resolve key: user input > environment variable
        resolved_key = (api_key.strip() if api_key else None) or os.getenv("OPENAI_API_KEY")
        
        if not resolved_key:
            raise ValueError("OpenAI API Key is required. Please provide it in the sidebar.")
        
        # Ensure a valid OpenAI model string is used
        valid_models = ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo"]
        selected_model = model_name if model_name in valid_models else "gpt-4o-mini"
        
        return ChatOpenAI(
            model=selected_model,
            api_key=resolved_key,
            temperature=0.7
        )

    elif provider == "ollama":
        selected_model = model_name or "llama3"
        return ChatOllama(
            model=selected_model,
            temperature=0.7
        )

    else:
        raise ValueError(f"Unsupported provider: '{provider}'")
