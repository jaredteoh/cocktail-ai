from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnableLambda
from config import LOCAL_MODEL_ID, TEMPERATURE

def get_llm(model_name=LOCAL_MODEL_ID, temperature=TEMPERATURE):
    """Return a cached Ollama LLaMA-3 model."""
    return Ollama(model=model_name, temperature=temperature)

PROMPT_TEMPLATE = PromptTemplate.from_template(
    """
    You are an expert cocktail assistant.
    
    User prompt: {prompt}
    User has the following ingredients: {ingredients}

    Task:
    1. *Section A* - List classic cocktails that can be made using only the available ingredients and match the user's request.
    2. *Section B* - List classic cocktails that require one or two additional ingredients and match the user's request.
        - Show the cocktail name.
        - Show the missing ingredient(s).
    
    For every cocktail in either section include:
    - Cocktail Name
    - List of ingredients with measurements
    - Instructions for preparation

    Use clear markdown headings:
    ## Section A: Ready Now
    ## Section B: Missing 1-2 Ingredients

    If no cocktails match, reply: "No cocktails can be made with the provided ingredients and preferences."
    """
)

def build_chain(llm):
    """Return a LangChain pipeline."""
    return (
        RunnableLambda(lambda d: {
            "prompt": d["prompt"],
            "ingredients": ", ".join(d["ingredients"])
        })
        | PROMPT_TEMPLATE
        | llm
    )
