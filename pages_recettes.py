import streamlit as st
import pandas as pd

def render_recipes_page(df: pd.DataFrame):
    st.header("\U0001F372 Recipes")

    
    # Filtres
    
    st.sidebar.subheader("\U0001F50D Filters")

    # Choix du mode de recherche 
    search_mode = st.sidebar.radio(
        "Search mode",
        ("By ingredients", "By recipe name")
    )

    # Liste d'ingrédients disponibles
    all_ingredients = sorted(
        {
            ing
            for lst in df["ingredients"]
            if isinstance(lst, list)
            for ing in lst
        }
    )

    # Liste des noms de recettes
    all_names = sorted(df["name"].dropna().unique().tolist())

    # MODE 1 : PAR NOM DE RECETTE

    if search_mode == "By recipe name":

        name_query = st.sidebar.text_input(
            "Recipe name :",
            "",
            help="Type the exact recipe name (or at least enough to find it)"
        )

       
        if not name_query.strip():
            st.info("\U0001F448 Type a recipe name in the sidebar to display it.")
            st.stop()

        # On cherche les recettes qui contiennent exactement ce texte
        filtered = df[df["name"].str.contains(name_query.strip(), case=False, na=False)]

        if filtered.empty:
            st.error("❌ No recipe found with this name.")
            st.stop()

        # On prend la première occurrence si plusieurs recettes ont le même nom
        recette = filtered.iloc[0]

        st.markdown("### \U0001F3AF Selected recipe")
        st.subheader(recette["name"])


        # Fiche détaillée directe


        # Description
        st.markdown("### \U0001F4DD Description")
        st.write(recette["description"])

        # Ingrédients
        st.markdown("### \U0001F9C2 Ingredients")
        if isinstance(recette["ingredients"], list):
            for ing in recette["ingredients"]:
                st.write(f"- {ing}")
        else:
            st.write("Ingredients unavailable for this recipe.")

        # Quantités
        st.markdown("### ⚖️ Quantities")
        if isinstance(recette["quantities"], list) and isinstance(recette["ingredients"], list) \
        and len(recette["quantities"]) == len(recette["ingredients"]):
            for q, i in zip(recette["quantities"], recette["ingredients"]):
                st.write(f"- **{i}** : {q}")
        else:
            st.warning("Quantities unavailable for this recipe.")

        # Instructions
        st.markdown("### 👩‍🍳 Steps")
        if isinstance(recette["instructions"], list):
            for step in recette["instructions"]:
                st.write(f"- {step}")
        else:
            st.write(recette["instructions"])

        # Nutrition 
        st.markdown("### \U0001F955 Nutritional information : ")

        cal = recette.get("calories", None)
        fat = recette.get("fat", None)
        sugar = recette.get("sugar", None)
        protein = recette.get("protein", None)

        def fmt(value, suffix=""):
            if value is None or (isinstance(value, (int, float)) and pd.isna(value)):
                return "N/A"
            v = round(float(value), 1)
            if v.is_integer():
                v = int(v)
            return f"{v}{suffix}"

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(f"""
            <div style='padding:15px; background-color:#95d5b2; border-radius:10px; text-align:center;'>
                <h4 style='margin-bottom:5px;'>\U0001F525 Calories</h4>
                <p style='font-size:20px; font-weight:600; margin:0;'>{fmt(cal, " kcal")}</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div style='padding:15px; background-color:#74c69d; border-radius:10px; text-align:center;'>
                <h4 style='margin-bottom:5px;'>\U0001F951 Fat</h4>
                <p style='font-size:20px; font-weight:600; margin:0;'>{fmt(fat, " g")}</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div style='padding:15px; background-color:#52b788; border-radius:10px; text-align:center;'>
                <h4 style='margin-bottom:5px;'>\U0001F9C1 Sugar</h4>
                <p style='font-size:20px; font-weight:600; margin:0;'>{fmt(sugar, " g")}</p>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
            <div style='padding:15px; background-color:#4aa87f; border-radius:10px; text-align:center;'>
                <h4 style='margin-bottom:5px;'>\U0001F357 Protein</h4>
                <p style='font-size:20px; font-weight:600; margin:0;'>{fmt(protein, " g")}</p>
            </div>
            """, unsafe_allow_html=True)

        return


    # MODE 2 : PAR INGRÉDIENTS


    # Multiselect ingrédients
    ingredient_filter = st.sidebar.multiselect(
        "Select at least 3 ingredients :",
        options=all_ingredients,
        help="Select at least 3 ingredients to see recipes."
    )

    if len(ingredient_filter) < 3:
        st.warning("\U0001F449 Select at least **3 ingredients** to begin with.")
        st.stop()

    # Temps max 
    temps_max = st.sidebar.number_input(
        "⌛ Maximum time (minutes) :",
        min_value=0,
        max_value=43552800,
        value=0,
        help="0 = no limit"
    )

    # Calories max 
    calories_max = st.sidebar.number_input(
        "\U0001F525 Maximum calories :",
        min_value=0,
        max_value=612855,
        value=0,
        help="0 =  no limit"
    )


    # Application des filtres 

    filtered = df.copy()

    # Ingrédients : la recette doit contenir TOUS les ingrédients choisis
    for ing in ingredient_filter:
        filtered = filtered[
            filtered["ingredients"].apply(
                lambda lst: isinstance(lst, list) and ing in lst
            )
        ]

    # Temps max 
    if temps_max > 0 and "total_time_min" in filtered.columns:
        filtered = filtered[filtered["total_time_min"] <= temps_max]

    # Calories max 
    if calories_max > 0 and "calories" in filtered.columns:
        filtered = filtered[filtered["calories"] <= calories_max]

    if filtered.empty:
        st.error("❌ No recipes found with these criteria.")
        st.stop()


    # Sélection aléatoire de 10 recettes

    if "sample_ids" not in st.session_state:
        st.session_state["sample_ids"] = []

    relancer = st.button("\U0001F501 Relaunch 10 new random recipes")

    if relancer or not st.session_state["sample_ids"]:
        sample = filtered.sample(
            n=min(10, len(filtered)), random_state=None
        )
        st.session_state["sample_ids"] = sample["id"].tolist()
    else:
        sample = filtered[filtered["id"].isin(st.session_state["sample_ids"])]

    st.markdown("### \U0001F3AF Recipes matching your criteria")


    # Affichage des cartes cliquables

    cols = st.columns(2)
    selected_id = st.session_state.get("selected_recipe_id", None)

    for idx, (_, row) in enumerate(sample.iterrows()):
        col = cols[idx % 2]
        with col:
            card = st.container(border=True)
            with card:

                st.markdown(f"**{row['name']}**")
                infos = []
                if "total_time_min" in row and row["total_time_min"] > 0:
                    infos.append(f"⏱️ {int(row['total_time_min'])} min")
                if "calories" in row and row["calories"] > 0:
                    infos.append(f"\U0001F525 {int(row['calories'])} kcal")
                if "rating" in row and row["rating"] > 0:
                    infos.append(f"⭐ {row['rating']:.1f}")
                if infos:
                    st.caption(" · ".join(infos))

                if st.button(
                    "See this recipe",
                    key=f"see_{row['id']}"
                ):
                    selected_id = row["id"]
                    st.session_state["selected_recipe_id"] = selected_id


    # Fiche détaillée (mode ingrédients)

    if selected_id is not None:
        try:
            selected_id_int = int(selected_id)
        except (ValueError, TypeError):
            selected_id_int = selected_id  

        current = filtered[filtered["id"] == selected_id_int]

        if current.empty:
            st.info(
                "The recipe you selected is no longer part of the results "
                "with the current filters."
                "Please select a recipe again from the list above."
            )
            st.session_state["selected_recipe_id"] = None

        else:
            recette = current.iloc[0]

            st.markdown("---")
            st.markdown("## \U0001F4C4 Details of the selected recipe")

            st.subheader(recette["name"])

            # Description
            st.markdown("### \U0001F4DD Description")
            st.write(recette["description"])

            # Ingredients
            st.markdown("### \U0001F9C2 Ingredients")
            if isinstance(recette["ingredients"], list):
                for ing in recette["ingredients"]:
                    st.write(f"- {ing}")
            else:
                st.write("Ingredients unavailable for this recipe.")

            # Quantities
            st.markdown("### ⚖️ Quantities")
            if isinstance(recette["quantities"], list) and isinstance(recette["ingredients"], list) \
            and len(recette["quantities"]) == len(recette["ingredients"]):
                for q, i in zip(recette["quantities"], recette["ingredients"]):
                    st.write(f"- **{i}** : {q}")
            else:
                st.warning("Quantities unavailable for this recipe.")

            # Instructions
            st.markdown("### 👩‍🍳 Steps")
            if isinstance(recette["instructions"], list):
                for step in recette["instructions"]:
                    st.write(f"- {step}")
            else:
                st.write(recette["instructions"])

            # Nutrition 
            st.markdown("### \U0001F955 Nutritional information : ")

            cal = recette.get("calories", None)
            fat = recette.get("fat", None)
            sugar = recette.get("sugar", None)
            protein = recette.get("protein", None)

            def fmt(value, suffix=""):
                if value is None or (isinstance(value, (int, float)) and pd.isna(value)):
                    return "N/A"
                v = round(float(value), 1)
                if v.is_integer():
                    v = int(v)
                return f"{v}{suffix}"

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.markdown(f"""
                <div style='padding:15px; background-color:#95d5b2; border-radius:10px; text-align:center;'>
                    <h4 style='margin-bottom:5px;'>\U0001F525 Calories</h4>
                    <p style='font-size:20px; font-weight:600; margin:0;'>{fmt(cal, " kcal")}</p>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div style='padding:15px; background-color:#74c69d; border-radius:10px; text-align:center;'>
                    <h4 style='margin-bottom:5px;'>\U0001F951 Fat</h4>
                    <p style='font-size:20px; font-weight:600; margin:0;'>{fmt(fat, " g")}</p>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                <div style='padding:15px; background-color:#52b788; border-radius:10px; text-align:center;'>
                    <h4 style='margin-bottom:5px;'>\U0001F9C1 Sugar</h4>
                    <p style='font-size:20px; font-weight:600; margin:0;'>{fmt(sugar, " g")}</p>
                </div>
                """, unsafe_allow_html=True)

            with col4:
                st.markdown(f"""
                <div style='padding:15px; background-color:#4aa87f; border-radius:10px; text-align:center;'>
                    <h4 style='margin-bottom:5px;'>\U0001F357 Protein</h4>
                    <p style='font-size:20px; font-weight:600; margin:0;'>{fmt(protein, " g")}</p>
                </div>
                """, unsafe_allow_html=True)



