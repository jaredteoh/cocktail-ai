import json

import streamlit as st
from config import INGREDIENTS_PATH

with open(INGREDIENTS_PATH, "r") as file:
    INGREDIENTS = json.load(file)

def ingredient_section(label, key, options):
    with st.expander(label, expanded=False):
        chosen = st.multiselect("Select:", options, key=f"{key}_sel")
        custom = st.text_input("Custom (comma-separated):", key=f"{key}_cus")
        if custom:
            chosen += [x.strip() for x in custom.split(",") if x.strip()]
    return chosen

def dedupe_and_normalize(items):
    return sorted({item.strip().lower() for item in items if item.strip()})

def display_inventory_by_category(inventory):
    categories = {
        "Base Spirits": INGREDIENTS.get("base_spirits", []),
        "Liqueurs": INGREDIENTS.get("liqueurs", []),
        "Bitters": INGREDIENTS.get("bitters", []),
        "Mixers": INGREDIENTS.get("mixers", []),
        "Garnishes": INGREDIENTS.get("garnishes", []),
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
