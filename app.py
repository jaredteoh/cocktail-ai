import json
from pathlib import Path

import streamlit as st
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough

# Paths and config
INGREDIENTS_PATH = Path("data/ingredients.json")
MODEL_ID = "llama3" 
TEMPERATURE = 0.6

# Load ingredients from JSON
if not INGREDIENTS_PATH.exists():
    st.error("Data file not found. Please ensure 'data/ingredients.json' exists.")
    st.stop()

with open(INGREDIENTS_PATH, "r") as file:
    ingredients = json.load(file)


# Streamlit App UI
st.title("CocktAIl - Your AI Cocktail Assistant")
st.markdown("#### Discover the perfect cocktail recipe based on your ingredients!")

user_inputs = {}

# Helper to render each category block
def ingredient_section(label, key, options):
    st.markdown(f"##### {label}")

    selected = st.multiselect(
        "Select from list:",
        options=options,
        key=f"{key}_select"
    )

    custom_input = st.text_input(
        "Others if not listed above (comma-separated):",
        key=f"{key}_custom"
    )

    if custom_input:
        custom_items = [item.strip() for item in custom_input.split(",") if item.strip()]
        selected.extend(custom_items)

    st.markdown("---")
    return selected

# Ingredient sections
user_inputs["base_spirits"] = ingredient_section(
    "Base Spirits",
    "base_spirits",
    ingredients.get("base_spirits", [])
)
user_inputs["liqueurs"] = ingredient_section(
    "Liqueurs",
    "liqueurs",
    ingredients.get("liqueurs", [])
)
user_inputs["bitters"] = ingredient_section(
    "Bitters",
    "bitters",
    ingredients.get("bitters", [])
)
user_inputs["mixers"] = ingredient_section(
    "Mixers",
    "mixers",
    ingredients.get("mixers", [])
)
user_inputs["garnishes"] = ingredient_section(
    "Garnishes",
    "garnishes",
    ingredients.get("garnishes", [])
)

# Combine all selected ingredients
all_ingredients = []
for category, items in user_inputs.items():
    all_ingredients.extend(items)

# Create LLM
@st.cache_resource(show_spinner="Loading local model...")
def load_llama3_local(model_name, temperature):
    return Ollama(model=model_name, temperature=temperature)
llm = load_llama3_local(model_name=MODEL_ID, temperature=TEMPERATURE)

prompt_template = PromptTemplate.from_template(
    # """
    # Generate a cocktail recipe for gin, lime, and sugar.
    # """
    """
    You are an expert cocktail assistant.
    
    User has the following ingredients: {ingredients}

    Your task:
    1. Identify as many classic cocktails as possible that can be made using ONLY the ingredients the user has provided.
    
    2. For each matching cocktail, output:
    - Cocktail Name
    - List of ingredients with measurements
    - Instructions for preparation

    3. Format the response as a clear list.

    If no cocktails match, reply: "No cocktails can be made with the provided ingredients."
    """
)

rag_chain = (
    {"ingredients": RunnablePassthrough()}
    | prompt_template
    | llm
)

if st.button("Find Cocktails"):
    if not all_ingredients:
        st.warning("Please select at least one ingredient.")
    else:
        ingredients_str = ", ".join(all_ingredients)
        with st.spinner("Generating response..."):
            response = rag_chain.invoke(ingredients_str)
        st.subheader("Cocktails You Can Make:")
        st.markdown(response)
