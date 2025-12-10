import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

def get_llm():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        # Fallback or error - returning a dummy compatible object or raising error
        # For this prototype, if no key, we might just return None and handle it in agents
        print("Warning: OPENAI_API_KEY not found.")
        return None
    
    return ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
