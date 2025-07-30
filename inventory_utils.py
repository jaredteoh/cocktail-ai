import json
import re
from fractions import Fraction

import streamlit as st
from config import INGREDIENTS_PATH

with open(INGREDIENTS_PATH, "r") as file:
    INGREDIENTS = json.load(file)

ML_PER_OZ = 30

UNICODE_FRACTIONS = {
    "¼": 0.25,
    "½": 0.5,
    "¾": 0.75,
    "⅐": 1/7,
    "⅑": 1/9,
    "⅒": 0.1,
    "⅓": 1/3,
    "⅔": 2/3,
    "⅕": 0.2,
    "⅖": 0.4,
    "⅗": 0.6,
    "⅘": 0.8,
    "⅙": 1/6,
    "⅚": 5/6,
    "⅛": 0.125,
    "⅜": 0.375,
    "⅝": 0.625,
    "⅞": 0.875,
}

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

def parse_number(token):
    token = token.strip()
    if token in UNICODE_FRACTIONS:
        return UNICODE_FRACTIONS[token]
    if "/" in token:
        return float(Fraction(token))
    return float(token)

def format_amount(value, unit):
    if unit == "oz":
        return f"{value:2g} oz"
    else:
        return f"{round(value)} ml"

def convert_units(markdown, to_unit):
    """
    Convert ml <-> oz inside a markdown string.
    Supports decimals, ASCII fractions, Unicode fractions.
    """
    
    pattern = r"(\d+(?:\.\d+)?|\d+\s*/\s*\d+|[¼½¾⅐⅑⅒⅓⅔⅕⅖⅗⅘⅙⅚⅛⅜⅝⅞])\s*(ml|oz)"
    
    def repl(match):
        num = parse_number(match.group(1))
        unit = match.group(2).lower()

        if unit == to_unit.lower():
            return match.group(0)
        
        if unit == "ml" and to_unit == "oz":
            return format_amount(num / ML_PER_OZ, "oz")
        if unit == "oz" and to_unit == "ml":
            return format_amount(num * ML_PER_OZ, "ml")
        return match.group(0)

    return re.sub(pattern, repl, markdown, flags=re.I)
