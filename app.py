import json
from pathlib import Path

import streamlit as st
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from llm_utils import get_llm, build_chain
from inventory_utils import (
    ingredient_section,
    dedupe_and_normalize,
    display_inventory_by_category,
    INGREDIENTS
)

st.set_page_config(page_title="CocktAIl", page_icon="🍸")

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

# Create LLM & chain
@st.cache_resource(show_spinner="Loading local model...")
def cached_chain():
    llm = get_llm()
    return build_chain(llm)

chain = cached_chain()

# Streamlit App UI
st.title("CocktAIl - Your AI Cocktail Assistant")
st.markdown("#### Discover the perfect cocktail recipe based on your ingredients!")

tab1, tab2 = st.tabs(["Inventory", "Cocktail Suggestions"])

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
            INGREDIENTS.get("base_spirits", [])
        )
    )
    inventory_selections.extend(
        ingredient_section(
            "Liqueurs",
            "liqueurs",
            INGREDIENTS.get("liqueurs", [])
        )
    )
    inventory_selections.extend(
        ingredient_section(
            "Bitters",
            "bitters",
            INGREDIENTS.get("bitters", [])
        )
    )
    inventory_selections.extend(
        ingredient_section(
            "Mixers",
            "mixers",
            INGREDIENTS.get("mixers", [])
        )
    )
    inventory_selections.extend(
        ingredient_section(
            "Garnishes",
            "garnishes",
            INGREDIENTS.get("garnishes", [])
        )
    )

    # Save inventory
    if st.button("Save Inventory"):
        st.session_state["inventory"] = dedupe_and_normalize(list(inventory_selections))

    st.subheader("Current Inventory")
    if st.session_state["inventory"]:
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
                response = chain.invoke(input_data)
            st.subheader("Cocktails You Can Make:")
            st.markdown(response)
