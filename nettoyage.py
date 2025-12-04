import pandas as pd

def clean_recipe_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nettoie le DataFrame des recettes :
    - garde uniquement les colonnes utiles
    - supprime les lignes vides / doublons
    - normalise quelques colonnes
    - renvoie un DataFrame prêt pour parsing + graphes
    """

    # 1) Colonnes utiles
    useful_cols = [
        "RecipeId", "Name", "RecipeCategory",
        "Description", "Images",
        "RecipeIngredientParts", "RecipeIngredientQuantities","RecipeInstructions",
        "AggregatedRating", "ReviewCount",
        "CookTime", "PrepTime", "TotalTime","Calories", "FatContent", "SugarContent", "ProteinContent",
    ]

    # 2) Intersect avec celles réellement présentes
    cols_to_keep = [c for c in useful_cols if c in df.columns]

    df = df[cols_to_keep].copy()

    # 3) Convertir les ratings en numéros si besoin
    if df["AggregatedRating"].dtype == "object":
        df["AggregatedRating"] = pd.to_numeric(df["AggregatedRating"], errors="coerce")

    # 4) Convertir ReviewCount en entier
    if "ReviewCount" in df.columns:
        df["ReviewCount"] = pd.to_numeric(df["ReviewCount"], errors="coerce").fillna(0).astype(int)

    # 5) Suppression des lignes sans nom / ingrédient / temps total
    df = df.dropna(subset=["Name"]).reset_index(drop=True)
    df = df.dropna(subset=["Description"]).reset_index(drop=True)

    # 6) Remplacer les NA NON critiques

    # Catégorie manquante -> Unknown
    if "RecipeCategory" in df.columns:
        df["RecipeCategory"] = df["RecipeCategory"].fillna("Unknown")

    # Note manquante -> 0 (affiché comme "Non noté")
    if "AggregatedRating" in df.columns:
        df["AggregatedRating"] = df["AggregatedRating"].fillna(0)

    # ReviewCount manquante -> 0
    if "ReviewCount" in df.columns:
        df["ReviewCount"] = (
            pd.to_numeric(df["ReviewCount"], errors="coerce")
              .fillna(0)
              .astype(int)
        )

    # 7) Suppression des doublons sur RecipeId ou Name
    if "RecipeId" in df.columns:
        df = df.drop_duplicates(subset=["RecipeId"])
    else:
        df = df.drop_duplicates(subset=["Name"])

    # 8) RENOMMAGE FINAL DES COLONNES 
    rename_map = {
        "RecipeId": "id",
        "Name": "name",
        "RecipeCategory": "category",
        "Description": "description",
        "Images": "images",
        "RecipeIngredientParts": "ingredients",
        "RecipeIngredientQuantities": "quantities",
        "RecipeInstructions": "instructions",
        "AggregatedRating": "rating",
        "ReviewCount": "reviews",
        "CookTime": "cook_time",
        "PrepTime": "prep_time",
        "TotalTime": "total_time",
        "Calories": "calories",
        "FatContent": "fat",
        "SugarContent": "sugar",
        "ProteinContent": "protein",
    }

    df = df.rename(columns=rename_map)

    return df
