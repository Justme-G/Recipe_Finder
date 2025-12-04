from html import unescape
import pandas as pd
import re
from nettoyage import clean_recipe_df


def detect_r_vector_columns(df: pd.DataFrame, n_check: int = 10):
    """
    Détecte les colonnes dont les données ressemblent à un vecteur R (c("...")).

    Paramètres :
    ------------
    df : pd.DataFrame
        Le DataFrame à analyser.
    n_check : int
        Nombre de lignes à échantillonner par colonne pour la détection (par défaut 10).

    Retour :
    --------
    list[str]
        Liste des noms de colonnes suspectées de contenir des vecteurs R.
    """
    cols_detected = []
    for col in df.columns:
        sample = df[col].dropna().astype(str).head(n_check)
        if sample.apply(lambda x: x.strip().startswith("c(")).any():
            cols_detected.append(col)
    return cols_detected

def parse_r_vector(s):
    """
    Convertit une chaîne du type c("a", "b", "c") en liste Python,
    en respectant les guillemets (ne coupe pas sur les virgules).
    """
    if not isinstance(s, str) or not s.strip().startswith("c("):
        return []
    # récupère tout ce qui est entre "..."
    return re.findall(r'"(.*?)"', s)


def apply_r_vectors(df: pd.DataFrame):
    df = df.copy()
    cols = detect_r_vector_columns(df)
    for col in cols:
        df[col] = df[col].apply(parse_r_vector)
    return df


#Nettoyage de la colonne ingrédients des &quote

def clean_ingredient_text(s: object) -> object:
    """
    Nettoie un nom d'ingrédient :
    - décode les entités HTML (&quot;, &amp;, ...)
    - retire les guillemets au début/à la fin
    """
    if not isinstance(s, str):
        return s
    s = unescape(s)          
    s = s.strip()
    
    if s.startswith('"') and s.endswith('"') and len(s) >= 2:
        s = s[1:-1].strip()
    return s


def clean_ingredients_list(lst):
    """Applique clean_ingredient_text à tous les éléments d'une liste."""
    if isinstance(lst, list):
        return [clean_ingredient_text(x) for x in lst]
    return lst


def clean_ingredients_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applique le nettoyage HTML sur la colonne 'ingredients'
    (liste de chaînes).
    """
    df = df.copy()
    if "ingredients" in df.columns:
        df["ingredients"] = df["ingredients"].apply(clean_ingredients_list)
    return df



# 1) Conversion d'une durée ISO-8601
def iso8601_to_hmin(s: object, zero_as="0Min") -> str:
    """
    Convertit une durée ISO-8601 (ex: PT24H, PT45M, PT24H45M, P1DT2H30M)
    en chaîne formatée du type '24H45Min', '24H', '45Min'.
    - zero_as : rendu si 0 minute (par défaut '0Min')
    """
    if not isinstance(s, str) or not s:
        return zero_as

    s = s.strip().upper()

    
    m = re.match(r"^P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$", s)
    if not m:
        
        return s

    days   = int(m.group(1) or 0)
    hours  = int(m.group(2) or 0)
    mins   = int(m.group(3) or 0)
    secs   = int(m.group(4) or 0)

    # Convertir jours en heures, et secondes en minutes 
    hours += days * 24
    mins  += secs // 60

    if hours and mins:
        return f"{hours}H{mins}Min"
    if hours:
        return f"{hours}H"
    if mins:
        return f"{mins}Min"
    return zero_as
    


def hmin_to_minutes(txt: str) -> int:
    if not isinstance(txt, str):
        return 0
    txt = txt.upper()
    h = re.search(r"(\d+)H", txt)
    m = re.search(r"(\d+)\s*MIN", txt)
    return (int(h.group(1)) if h else 0) * 60 + (int(m.group(1)) if m else 0)

# 2) Application à plusieurs colonnes du DataFrame
def format_time_columns(df: pd.DataFrame,
                        cols=("cook_time", "prep_time", "total_time")):
    """
    Formate les colonnes ISO-8601 en texte '...H...Min'.
    Optionnel : ajoute aussi des colonnes numériques en minutes pour trier/filtrer.
    """
    df = df.copy()
    for c in cols:
        if c in df.columns:
            df[c] = df[c].apply(iso8601_to_hmin)
            df[f"{c}_min"] = df[c].apply(hmin_to_minutes)
    return df


