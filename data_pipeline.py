import pandas as pd
import streamlit as st
from nettoyage import clean_recipe_df
from forme_list import apply_r_vectors, format_time_columns, clean_ingredients_column


CSV_URL="https://github.com/Justme-G/Recipe_Finder/releases/download/v1.0.0/recipes.csv"

@st.cache_data
def load_recipes() -> pd.DataFrame:
    """
    Pipeline complet : lit, nettoie, parse, convertit.
    Renvoie un DataFrame final et propre.
    """
    df = pd.read_csv(CSV_URL)

    # 1. Nettoyage
    df = clean_recipe_df(df)

    # 2. Parsing des vecteurs R (ingredients, quantities)
    df = apply_r_vectors(df)

    # 3. Nettoyage des noms d'ingrédients (suppression de &quot;, guillemets, etc.)
    df = clean_ingredients_column(df)

    # 4. Formatage des temps + colonnes minutes
    df = format_time_columns(df)

    return df