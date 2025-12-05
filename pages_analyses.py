import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np


def render_global_analysis_page(df):


    data = df.copy()

    # On prépare une colonne "n_ingredients" pour les graphes
    def count_ingredients(val):
        if isinstance(val, list):
            return len(val)
        elif isinstance(val, str):
            return len([x for x in val.split(",") if x.strip()])
        else:
            return np.nan

    data["n_ingredients"] = data["ingredients"].apply(count_ingredients)


    st.header("\U0001F4CA Overall analysis of recipes")




    # Recettes les plus populaires

    st.subheader("Most popular recipes")

    col1, col2 = st.columns([0.8, 3])

    with col1:

        min_reviews = st.slider(
            "Minimum number of reviews",
            min_value=0,
            max_value=1400,
            value=50,
            step=10,)

        top_n = st.slider(
            "Number of recipes to display",
            min_value=5,
            max_value=30,
            value=20,
            step=5,)

    with col2:
        pop = data[data[["rating", "reviews"]].notna().all(axis=1)].copy()
        pop = pop[pop["reviews"] >= min_reviews]


        pop["pop_score"] = pop["rating"] * np.log1p(pop["reviews"])

        top_pop = (
            pop.sort_values("pop_score", ascending=False)
            .head(top_n)
            .sort_values("pop_score")
        )

        if top_pop.empty:
            st.info("No recipes comply with popularity filters.")
        else:
            fig = px.bar(
                top_pop,
                x="pop_score",
                y="name",
                orientation="h",
                color="rating",
                hover_data=["reviews", "category"],
                title="Top popular recipes",
                color_continuous_scale=["#b7e4c7", "#74c69d", "#4aa87f"],
            )
            fig.update_layout(
                xaxis_title="Popularity score",
                yaxis_title="Recipes",
                title_x=0.4,
                coloraxis_colorbar_title="Note",
                plot_bgcolor="#5e8667",      
                paper_bgcolor="#5e8667",     
                font_color="black",
                margin=dict(l=250),
            )
            fig.update_yaxes(
            tickmode="linear",  
            dtick=1
            )
            st.plotly_chart(fig, width='stretch')

    st.markdown("---")


    # Temps moyen par catégorie

    st.subheader("Average time per category")

    col_chart, col_filters = st.columns([4, 1])

    with col_filters:
        
        
        min_recipes = st.slider(
            "Minimum number of recipes per category",
            min_value=100,
            max_value=200,
            value=150,
            step=10,
        )

        
        n_cats = st.slider(
            "Number of categories to display",
            min_value=5,
            max_value=30,
            value=15,
            step=5,
        )

    with col_chart:

        #Ici on supprime les catégories qui représente un durée de préparation
        data_clean = data[~data["category"].str.contains("<", na=False)].copy()

        counts = data_clean["category"].value_counts()

        # on garde les catégories avec assez de recettes
        valid_cats = counts[counts >= min_recipes].index


        mean_time = (
            data_clean[data_clean["category"].isin(valid_cats)]
            .groupby("category")["total_time_min"]
            .mean()
            .reset_index()
        )

        
        mean_time = (
            mean_time.sort_values("total_time_min")
            .head(n_cats)
            .sort_values("total_time_min")
        )

        
        mean_time["category_short"] = mean_time["category"].apply(
            lambda x: x if len(x) <= 30 else x[:27] + "..."
        )

        if mean_time.empty:
            st.info("No categories match the filters.")
        else:
            fig = px.bar(
                mean_time,
                x="total_time_min",
                y="category_short",
                orientation="h",
                title="Total average time required (by category)",
                color="total_time_min",
                color_continuous_scale=["#b7e4c7", "#74c69d", "#4aa87f"],
            )

            fig.update_layout(
                xaxis_title="Average total time (min)",
                yaxis_title="Category",
                title_x=0.3,
                plot_bgcolor="#5e8667",
                paper_bgcolor="#5e8667",
                font_color="white",
                margin=dict(l=220),
                coloraxis_colorbar_title="Time (min)",
            )

            fig.update_yaxes(
                tickmode="linear",
                dtick=1,
                tickfont=dict(size=11),
            )

            st.plotly_chart(fig, width='stretch')

    st.markdown("---")


    # Popularité vs calories (bubble chart)

    st.subheader("Popularity vs Calories")

    col_filters, col_chart = st.columns([1, 4])

    with col_filters:
        
        min_reviews_pop = st.slider(
            "Minimum number of reviews",
            min_value=600,
            max_value=1500,
            value=1000,
            step=5,
        )

        max_cal_pop = st.slider(
            "Maximum calories",
            min_value=1000,
            max_value=3000,
            value=1500,
            step=50,
        )

        max_points = st.slider(
            "Maximum number of recipes to display",
            min_value=100,
            max_value=400,
            value=250,
            step=100,
        )

    with col_chart:
        bubble = data[
            data[["rating", "reviews", "calories", "total_time_min"]].notna().all(axis=1)].copy()

        bubble = bubble[
            (bubble["reviews"] >= min_reviews_pop)
            & (bubble["calories"] <= max_cal_pop)
            & (bubble["calories"] > 0)
            & (bubble["total_time_min"] > 0)
        ]

        
        if len(bubble) > max_points:
            bubble = bubble.sample(max_points, random_state=42)

        if bubble.empty:
            st.info("No recipe matches the selected filters.")
        else:
            fig = px.scatter(
                bubble,
                x="calories",
                y="rating",
                size="reviews",
                color="total_time_min",
                hover_name="name",
                hover_data=["category", "reviews", "total_time_min"],
                title="Popularity vs Calories",
                color_continuous_scale=["#b7e4c7", "#74c69d", "#4aa87f"],
            ) 

            fig.update_layout(
                xaxis_title="Calories",
                yaxis_title="Rating",
                title_x=0.4,
                plot_bgcolor="#5e8667",
                paper_bgcolor="#5e8667",
                font_color="white",
                coloraxis_colorbar_title="Total time (min)",
            )
            fig.update_yaxes(constrain='domain',
                            range=[data["rating"].min() - 0.1,data["rating"].max() + 0.1])


            st.plotly_chart(fig, width='stretch')
            st.markdown("<p style='text-align:center; color:#ffffff; opacity:0.8;'>The size of the bubbles represents the number of reviews.</p>",
            unsafe_allow_html=True
        )

    st.markdown("---")


 
    # Nutrition profiles by category 

    st.subheader("Nutrition profiles by category")

    nutri_cols = ["fat", "sugar", "protein"]

    
    nutri_mean = (
        data.groupby("category")[nutri_cols]
        .mean(numeric_only=True)
        .dropna()
    )
    if nutri_mean.empty:
        st.warning("No nutritional data available to build this chart.")
    else:
        all_cats = sorted(nutri_mean.index.tolist())

        selected_cats = st.multiselect(
            "Select categories to compare (Maximum 5)",
            options=all_cats,
            default=[],
            max_selections=5,
        )

        if not selected_cats:
            st.info("Select at least one category.")
        else:
        
            mat = nutri_mean.loc[selected_cats, nutri_cols]

            if mat.empty:
                st.warning("No nutritional data for the selected categories.")
            else:
       
                mat_display = mat.round(0)

        
                fig = px.imshow(
                    mat_display,
                    x=nutri_cols,
                    y=selected_cats,
                    color_continuous_scale=["#b7e4c7", "#74c69d", "#40916c"],
                    aspect="auto",
                    text_auto=True, 
                    labels=dict(x="Metric", y="Category", color="Value"),
                    title="Average nutritional values by category",
                )

                fig.update_layout(
                    title_x=0.4,
                    plot_bgcolor="#5e8667",
                    paper_bgcolor="#5e8667",
                    font_color="white",
                    coloraxis_colorbar_title="Value",
                    margin=dict(l=120, r=40, t=60, b=40),
                )

        
                fig.data[0].text = mat_display.values
                fig.data[0].texttemplate = "%{text}"

                st.plotly_chart(fig, width='stretch')
                st.markdown("<p style='text-align:center; color:#ffffff; opacity:0.8;'>Here, all values are given in grams.</p>",
                    unsafe_allow_html=True
                )

    st.markdown("---")




    # Score composite Qualité / Temps / Calories (top recettes)

    st.subheader("Optimised recipes in Quality / Time / Calories")

    col_filters, col_chart = st.columns([1, 4])

    with col_filters:
        
        
        top_n = st.slider(
            "Number of recipes to display",
            min_value=5,
            max_value=15,
            value=10,
            step=5,
    )

    with col_chart:
       
        score_df = data[
            data[["rating", "total_time_min", "calories"]].notna().all(axis=1)
        ].copy()
        score_df = score_df[
            (score_df["total_time_min"] > 0)
            & (score_df["calories"] > 0)
    ]

        if score_df.empty:
            st.info("No recipes comply with the current filters.")
        else:
            
            def norm_col(s):
                s = s.astype(float)
                denom = s.max() - s.min()
                if denom == 0:
                    return s * 0 + 0.5
                return (s - s.min()) / denom

            score_df["rating_norm"] = norm_col(score_df["rating"]) 
            score_df["time_norm"] = 1 / score_df["total_time_min"]
            score_df["time_norm"] = norm_col(score_df["time_norm"])
            score_df["cal_norm"] = 1 / score_df["calories"]
            score_df["cal_norm"] = norm_col(score_df["cal_norm"])

           
            score_df["score"] = (
                0.4 * score_df["rating_norm"]
                + 0.3 * score_df["time_norm"]
                + 0.3 * score_df["cal_norm"]
        )

            top = (
                score_df.sort_values("score", ascending=False)
                .head(top_n)
                .sort_values("score")
        )

            
            top["name_short"] = top["name"].apply(
                lambda x: x if len(x) <= 40 else x[:37] + "..."
        )
            
            fig = px.bar(
                top,
                x="score",
                y="name_short",
                orientation="h",
                title="Top optimised recipes (quality / time / calories)",
                color="score",
                color_continuous_scale=["#b7e4c7", "#74c69d", "#4aa87f"],
                hover_data=["name", "rating", "total_time_min", "calories"],
        )

            fig.update_layout(
                xaxis_title="Composite score ",
                yaxis_title="Recipes",
                title_x=0.3,
                plot_bgcolor="#5e8667",
                paper_bgcolor="#5e8667",
                font_color="white",
                margin=dict(l=250),
                coloraxis_colorbar_title="Score",
        )

            fig.update_yaxes(
                tickmode="linear",
                dtick=1,
                tickfont=dict(size=11),
        )

            st.plotly_chart(fig, width='stretch')

            st.markdown("<p style='text-align:center; color:#ffffff; opacity:0.8;'>This chart shows the fastest, most balanced and highest-rated recipes.</p>",
            unsafe_allow_html=True
        )