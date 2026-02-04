import pandas as pd
import streamlit as st
from pathlib import Path
import requests

from nettoyage import clean_recipe_df
from forme_list import apply_r_vectors, format_time_columns, clean_ingredients_column

CSV_URL = "https://github.com/Justme-G/Recipe_Finder/releases/download/v1.1.0/recipes_small.csv"

BASE_DIR = Path(__file__).resolve().parent
LOCAL_REPO_CSV = BASE_DIR / "recipes_small.csv"

DATA_DIR = Path.home() / ".recipe_finder"
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOCAL_DOWNLOADED = DATA_DIR / "recipes_small.csv"


def download_once(url: str, dest: Path) -> Path:
    if dest.exists() and dest.stat().st_size > 0:
        return dest

    r = requests.get(url, stream=True, timeout=120)
    r.raise_for_status()

    tmp = dest.with_suffix(".tmp")
    with open(tmp, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024 * 1024):
            if chunk:
                f.write(chunk)

    tmp.replace(dest)
    return dest


@st.cache_data(show_spinner=True)
def load_recipes() -> pd.DataFrame:
    """
    Pipeline complet : lit, nettoie, parse, convertit.
    Renvoie un DataFrame final et propre.
    """

    # 👉 priorité au fichier dans le repo s'il existe
    if LOCAL_REPO_CSV.exists():
        csv_path = LOCAL_REPO_CSV
    else:
        csv_path = download_once(CSV_URL, LOCAL_DOWNLOADED)

    df = pd.read_csv(csv_path)

    # 1. Nettoyage
    df = clean_recipe_df(df)

    # 2. Parsing des vecteurs R (ingredients, quantities)
    df = apply_r_vectors(df)

    # 3. Nettoyage des noms d'ingrédients
    df = clean_ingredients_column(df)

    # 4. Formatage des temps + colonnes minutes
    df = format_time_columns(df)

    return df
