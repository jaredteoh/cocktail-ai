import json
from pathlib import Path

import streamlit as st
from rag_utils import create_vector_index, load_vector_index
# from langchain_community.chat_models import ChatOpenAI
# from langchain_google_genai import GoogleGenerativeAI
# from langchain_community.llms import HuggingFaceHub
# from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
# from langchain_huggingface.llms.huggingface_pipeline import HuggingFacePipeline
# from langchain_community.llms import HuggingFacePipeline
from langchain_community.llms import Ollama
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.schema.runnable import RunnablePassthrough, RunnableLambda

# Paths and config
# EPUB_PATH = Path("data/cocktail_recipe.epub")
# INDEX_PATH = Path("indexes/cocktail_index")
INGREDIENTS_PATH = Path("data/ingredients.json")
# MODEL_ID = "google/flan-t5-base" 
# MAX_NEW_TOKENS = 512
# TEMPERATURE = 0.6

# # Ensure recipe file exists
# if not EPUB_PATH.exists():
#     st.error("EPUB file not found. Please ensure 'data/cocktail_recipe.epub' exists.")
#     st.stop()

# # Create index if not already created
# if not (INDEX_PATH / "index.faiss").exists():
#     with st.spinner("Creating vector index..."):
#         create_vector_index(str(EPUB_PATH))
#     st.success("Vector index created successfully!")

# # Load index
# with st.spinner("Loading vector index..."):
#     vector_index = load_vector_index()

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
# user_inputs["equipment"] = ingredient_section(
#     "Equipment",
#     "equipment",
#     ingredients.get("equipment", [])
# )
# user_inputs["glassware"] = ingredient_section(
#     "Glassware",
#     "glassware",
#     ingredients.get("glassware", [])
# )

# Combine all selected ingredients
all_ingredients = []
for category, items in user_inputs.items():
    all_ingredients.extend(items)

# Create LLM
# llm = ChatOpenAI(
#     temperature=0.3,
#     model="gpt-3.5-turbo",
#     openai_api_key=st.secrets["OPENAI_API_KEY"]
# )
# llm = GoogleGenerativeAI(
#     model="models/text-bison-001",
#     google_api_key=st.secrets["GOOGLE_API_KEY"],
#     temperature=0.6
# )
# llm = HuggingFaceHub(
#     # repo_id="google/flan-t5-small",
#     repo_id="meta-llama/Meta-Llama-3-8B-Instruct",
#     # task="text-generation",
#     model_kwargs={"temperature": 0.6, "max_length": 512},
#     huggingfacehub_api_token=st.secrets["HUGGINGFACEHUB_API_TOKEN"]
# )
# @st.cache_resource(show_spinner="Loading local model...")
# def load_local_llm(model_id):
#     tokenizer = AutoTokenizer.from_pretrained(model_id, use_fast=True)
#     model = AutoModelForSeq2SeqLM.from_pretrained(model_id)
#     local_pipeline = pipeline(
#         "text2text-generation",
#         model=model,
#         tokenizer=tokenizer,
#         max_length=MAX_NEW_TOKENS,
#         temperature=TEMPERATURE,
#     )
#     return HuggingFacePipeline(pipeline=local_pipeline)
# llm = load_local_llm(MODEL_ID)
@st.cache_resource(show_spinner="Loading local model...")
def load_llama3_local(model_name="llama3"):
    return Ollama(model=model_name)
llm = load_llama3_local()

# prompt_template = PromptTemplate.from_template(
#     """
#     You are an expert cocktail assistant.

#     Here are some cocktail recipes extracted from a book:

#     {context}

#     User has the following ingredients: {ingredients}
    
#     Your task:
#     1. From the recipes above, identify all cocktails that can be made *using ONLY* the ingredients the user has provided.
    
#     2. For each matching cocktail, output:
#     - Cocktail Name
#     - List of ingredients with measurements (exclude equipment or glassware)

#     3. Format the response as a clear list.

#     If no cocktails match, reply: "No cocktails can be made with the provided ingredients."
#     """
# )
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

# retriever = vector_index.as_retriever(search_kwargs={"k": 5})
# context_retriever = (
#     vector_index.as_retriever(search_kwargs={"k": 5})
#     | RunnableLambda(lambda docs: "\n\n".join([doc.page_content for doc in docs]))
# )
rag_chain = (
    # {"context": retriever, "ingredients": RunnablePassthrough()}
    # {"context": context_retriever, "ingredients": RunnablePassthrough()}
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
