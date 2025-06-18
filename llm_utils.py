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

    Based on both the user's preferences and ingredients:
    1. Suggest classic cocktails that can be made using ONLY the ingredients and match the user's request.
    
    2. For each cocktail, output:
    - Cocktail Name
    - List of ingredients with measurements
    - Instructions for preparation

    3. Format the response as a clear list.

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
