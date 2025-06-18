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

# Create LLM
@st.cache_resource(show_spinner="Loading local model...")
def load_llama3_local(model_name, temperature):
    return Ollama(model=model_name, temperature=temperature)
llm = load_llama3_local(model_name=MODEL_ID, temperature=TEMPERATURE)

prompt_template = PromptTemplate.from_template(
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

def combine_prompt_and_ingredients(data):
    return {
        "prompt": data["prompt"],
        "ingredients": ", ".join(data["ingredients"])
    }

rag_chain = (
    RunnablePassthrough(combine_prompt_and_ingredients)
    | prompt_template
    | llm
)

# Streamlit App UI
st.title("CocktAIl - Your AI Cocktail Assistant")
st.markdown("#### Discover the perfect cocktail recipe based on your ingredients!")

tab1, tab2 = st.tabs(["Inventory", "Cocktail Suggestions"])

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

# Tab 1: Inventory
with tab1:
    st.header("Your Ingredient Inventory")

    if "inventory" not in st.session_state:
        st.session_state["inventory"] = []

    inventory_selections = []
    inventory_selections.extend(
        ingredient_section(
            "Base Spirits",
            "base_spirits",
            ingredients.get("base_spirits", [])
        )
    )
    inventory_selections.extend(
        ingredient_section(
            "Liqueurs",
            "liqueurs",
            ingredients.get("liqueurs", [])
        )
    )
    inventory_selections.extend(
        ingredient_section(
            "Bitters",
            "bitters",
            ingredients.get("bitters", [])
        )
    )
    inventory_selections.extend(
        ingredient_section(
            "Mixers",
            "mixers",
            ingredients.get("mixers", [])
        )
    )
    inventory_selections.extend(
        ingredient_section(
            "Garnishes",
            "garnishes",
            ingredients.get("garnishes", [])
        )
    )

    # Save inventory
    if st.button("Save Inventory"):
        st.session_state["inventory"] = list(set(inventory_selections))  # Remove duplicates

    st.subheader("Current Inventory")
    if st.session_state["inventory"]:
        st.success(", ".join(st.session_state["inventory"]))
    else:
        st.info("No ingredients selected yet.")

# Tab 2: Prompt-based Suggestions
with tab2:
    st.header("Smart Cocktail Recommender")

    prompt = st.text_input("Describe what you're in the mood for (e.g. 'I want something sweet and refreshing')")

    if st.button("Suggest Cocktails"):
        if not prompt:
            st.warning("Please enter a prompt describing what you want.")
        elif not st.session_state["inventory"]:
            st.warning("Your inventory is empty. Add ingredients in the Inventory tab.")
        else:
            input_data = {
                "prompt": prompt,
                "ingredients": st.session_state["inventory"]
            }
            with st.spinner("Generating response..."):
                response = rag_chain.invoke(input_data)
            st.subheader("Cocktails You Can Make:")
            st.markdown(response)
