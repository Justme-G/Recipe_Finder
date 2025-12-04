import streamlit as st
from data_pipeline import load_recipes
from pages_recettes import render_recipes_page
from pages_analyses import render_global_analysis_page

st.markdown(
    """
    <style>
        /* Limiter la hauteur de TOUTES les listes de suggestions (select / multiselect) */
        div[role="listbox"] {
            max-height: 200px !important;
            overflow-y: auto !important;
        }

        /* Sécurité : si un wrapper interne impose une hauteur auto */
        div[data-baseweb="popover"] > div {
            max-height: 220px !important;
            overflow-y: auto !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)



st.set_page_config(page_title="Recipes Finder",page_icon="🍽️",layout="wide")

st.markdown("""
<style>

/* Couleur de la ligne active */
[data-baseweb="slider"] > div > div {
    background-color: #5e8667 !important;
}



</style>
""", unsafe_allow_html=True)



@st.cache_data
def load_data():
    return load_recipes()



# STYLE GLOBAL
st.markdown(
    """
    <style>
        /* Couleur de fond */
        .stApp {
            background-color: #8ab694 ;  /* Vert pale */
        }

        /* Couleur du titre */
        h1 {
            color: #000000;  /* Noir */
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        }
    </style>
    """,
    unsafe_allow_html=True)

st.title ("\U0001F373 Find the recipes that suits you") # 🍳
st.write("Welcome to your recipe app.")
st.write("Use the menu on the left to navigate through the pages.")

# SIDEBAR : NAVIGATION + FILTRES


st.sidebar.markdown(
    "<p style='font-size:22px; font-weight:600;'>\U0001F37D Navigation</p>",
    unsafe_allow_html=True
)

page = st.sidebar.radio(
    "",
    ("Home", "Recipes", "Overall analysis")
)

df = None
if page in ("Recipes", "Overall analysis") : 
    df = load_data()
# ACCUEIL


if page == "Home":
    
    st.subheader("Find recipe ideas based on whatever you have on hand.")

    
    st.markdown(
        """
        Welcome to **Recipe Finder** \U0001F44B  

        This application allows you to :
        - filter recipes based on **your ingredients** available ,
        - set a **maximum preparation time**,
        - set a **calorie limit** per recipe,
        - explore a selection of **random recipes** matching your criteria,
        - view **analyses** of all recipes.

        Use the menu on the left to :
        - \U0001F449 go to the **Recipes** page and start a search,
        - \U0001F4CA explore the charts on the **Analysis** page.
        """
    )

    st.markdown("---")

    
    st.header("\U0001F9E9 How does it work?")
    st.markdown(
        """
        1. **Select your main ingredients** from the sidebar (at least 3).
        2. Specify a **maximum time** and a **calorie limit** (Optional).
        3. Go on the **Recipes** page to see a selection of dishes that match your criteria.
        4. Click on a recipe to view its detailed description :  
           *ingredients, quantities, description, steps, image, and nutritional information*.
        """
    )

    st.markdown("---")


   
    st.markdown("### ⭐ Key features")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div style='padding:15px; background-color:#b7e4c7; border-radius:10px; text-align:center;'>
            <h3>\U0001F50D Search</h3>
            <p>Find recipes based on your available ingredients, time and calories.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style='padding:15px; background-color:#a3d8b8; border-radius:10px; text-align:center;'>
            <h3>\U0001F4C4 Recipe Details</h3>
            <p>Images, instructions, nutrition and user ratings for each recipe.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div style='padding:15px; background-color:#8ccfa6; border-radius:10px; text-align:center;'>
            <h3>\U0001F4CA Analysis</h3>
            <p>Explore global statistics and trends across thousands of recipes.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("## Why use Recipe Finder?")
    st.markdown("""
    - Save **time** by instantly filtering thousands of recipes  
    - Avoid recipes that are too long or too caloric  
    - Get **inspiration** when you don't know what to cook  
    - Discover new categories and flavors  
    """)


    st.markdown("""
    <br><hr>
    <p style='text-align:center; color:#444;'>
    Made with ❤️ using Streamlit — University Project (2025)
    </p>
    """, unsafe_allow_html=True)

# RECETTES 
elif page == "Recipes":
    render_recipes_page(df)

# ANALYSE GLOBALE
elif page == "Overall analysis":
    render_global_analysis_page(df)


