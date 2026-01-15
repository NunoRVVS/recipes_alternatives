import streamlit as st
import requests
import json

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Flavor Fusion AI",
    page_icon="🍳",
    layout="centered"
)

# The URL where your FastAPI backend is running
API_URL = "http://localhost:8000"

# --- SESSION STATE ---
# To remember the last generated recipe and its ID
if 'recipe_data' not in st.session_state:
    st.session_state.recipe_data = None
if 'recipe_id' not in st.session_state:
    st.session_state.recipe_id = None

# --- HELPER FUNCTIONS ---
def parse_recipe_text(text):
    """A simple helper to format the AI's text response for display."""
    # In a more robust app, you'd use regex or expect JSON from the AI
    # For now, we'll just display the raw text in a formatted way.
    return text

# --- UI LAYOUT ---
st.markdown("<h1 style='text-align: center;'>🍳 Flavor Fusion AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Create and transform recipes with the power of AI.</p>", unsafe_allow_html=True)
st.divider()

st.subheader("1. Create a Base Recipe")

with st.form("new_recipe_form"):
    title = st.text_input("Recipe Title", placeholder="E.g., Classic Chicken Soup")
    ingredients = st.text_area("Ingredients", placeholder="- 1 lb Chicken\n- 4 cups Chicken Broth\n- 1 cup Carrots, chopped")
    instructions = st.text_area("Instructions", placeholder="1. Boil chicken in broth.\n2. Add carrots and simmer...")
    
    submitted = st.form_submit_button("Save Recipe", type="primary")

if submitted:
    if not all([title, ingredients, instructions]):
        st.warning("Please fill out all fields to save a recipe.")
    else:
        # The ingredients are a single string, split them into a list
        ingredients_list = [item.strip() for item in ingredients.split('\n') if item.strip()]
        
        recipe_payload = {
            "title": title,
            "ingredients": ingredients_list,
            "instructions": instructions
        }
        
        with st.spinner("Saving your recipe to the database..."):
            try:
                response = requests.post(f"{API_URL}/recipes/", json=recipe_payload)
                if response.status_code == 200:
                    result = response.json()
                    st.session_state.recipe_id = result.get("id")
                    st.session_state.recipe_data = recipe_payload # Store the full recipe data
                    st.success(f"Recipe '{title}' saved with ID: {st.session_state.recipe_id}!")
                else:
                    st.error(f"Failed to save recipe. Server responded with: {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("Connection Error: Could not connect to the backend API. Is it running?")

# --- DISPLAY AND TRANSFORM SECTION ---
if st.session_state.recipe_data:
    st.divider()
    st.subheader("2. View and Transform Your Recipe")

    # Display the current recipe
    with st.container(border=True):
        st.markdown(f"#### {st.session_state.recipe_data['title']}")
        st.markdown("**Ingredients:**")
        # Create a bulleted list from the ingredients
        st.markdown("\n".join(f"- {ing}" for ing in st.session_state.recipe_data['ingredients']))
        st.markdown("**Instructions:**")
        st.write(st.session_state.recipe_data['instructions'])

    # Transformation options
    st.write("") # Spacer
    transformation = st.selectbox(
        "Choose a transformation:",
        ["", "Vegetarian", "Vegan", "Gluten-Free", "Spicy", "Low-Carb"],
        key="transformation_choice"
    )

    if st.button(f"Transform to {transformation}", disabled=(not transformation)):
        with st.spinner(f"AI is creating a {transformation} version..."):
            try:
                # Call your FastAPI transform endpoint
                response = requests.post(
                    f"{API_URL}/recipes/{st.session_state.recipe_id}/transform?transformation_type={transformation}"
                )
                if response.status_code == 200:
                    transformed_recipe_text = response.json()['transformed_recipe']
                    
                    # Display the new recipe
                    st.success("Transformation complete!")
                    st.subheader(f"✨ Transformed: {transformation} Version")
                    with st.container(border=True, height=300):
                         st.markdown(parse_recipe_text(transformed_recipe_text))
                else:
                    st.error(f"Transformation failed. Server responded with: {response.text}")

            except requests.exceptions.ConnectionError:
                st.error("Connection Error: Could not connect to the backend API.")
