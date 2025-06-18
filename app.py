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

#Streamlit configuration
st.markdown(
    """
    <style>
      .stButton>button { width: 100%; }
      .stTabs [role="tab"] { font-weight: 600; }
    </style>
    """,
    unsafe_allow_html=True,
)

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
    with st.expander(label, expanded=False):
        chosen = st.multiselect("Select:", options, key=f"{key}_sel")
        custom = st.text_input("Custom (comma-separated):", key=f"{key}_cus")
        if custom:
            chosen += [x.strip() for x in custom.split(",") if x.strip()]
    return chosen

# Helper to dedepuplicate and normalize ingredient selections
def dedupe_and_normalize(items):
    return sorted({item.strip().lower() for item in items if item.strip()})

# Helper to display inventory by category
def display_inventory_by_category(inventory):
    categories = {
        "Base Spirits": ingredients.get("base_spirits", []),
        "Liqueurs": ingredients.get("liqueurs", []),
        "Bitters": ingredients.get("bitters", []),
        "Mixers": ingredients.get("mixers", []),
        "Garnishes": ingredients.get("garnishes", []),
    }

    categorized = {cat: [] for cat in categories}
    others = []

    for item in inventory:
        found = False
        for cat, known_items in categories.items():
            if item in map(str.lower, known_items):
                categorized[cat].append(item)
                found = True
                break
        if not found:
            others.append(item)

    for cat, items in categorized.items():
        if items:
            st.markdown(f"**{cat}:**")
            st.markdown(", ".join(sorted(i.title() for i in items)))

    if others:
        st.markdown("**Others:**")
        st.markdown(", ".join(sorted(i.title() for i in others)))

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
        st.session_state["inventory"] = dedupe_and_normalize(list(inventory_selections))

    st.subheader("Current Inventory")
    if st.session_state["inventory"]:
        # st.success(", ".join(st.session_state["inventory"]))
        display_inventory_by_category(st.session_state["inventory"])
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
