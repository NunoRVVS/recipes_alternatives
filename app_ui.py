import streamlit as st
import json
from google import genai
from google.genai import types

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Recipes Alternatives AI",
    page_icon="🍳",
    layout="centered"
)

# --- API SETUP ---
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except (FileNotFoundError, KeyError):
    st.error("GOOGLE_API_KEY not found in secrets. Please add it in .streamlit/secrets.toml or Streamlit Cloud Secrets.")
    st.stop()

client = genai.Client(api_key=GOOGLE_API_KEY)

# --- SESSION STATE ---
# To remember the last generated recipe and its ID
if 'recipe_data' not in st.session_state:
    st.session_state.recipe_data = None
if 'recipe_id' not in st.session_state:
    st.session_state.recipe_id = None

# --- HELPER FUNCTIONS ---
def parse_recipe_text(recipe_data):
    """Formats the recipe dictionary into a Markdown string."""
    if isinstance(recipe_data, str):
        return recipe_data
        
    return f"#### {recipe_data.get('title', 'Untitled')}\n\n**Ingredients:**\n" + \
           "\n".join(f"- {ing}" for ing in recipe_data.get('ingredients', [])) + \
           f"\n\n**Instructions:**\n{recipe_data.get('instructions', '')}"

# --- UI LAYOUT ---
col1, col2 = st.columns([1, 5])
with col1:
    st.image("images/recipe_icon.png", width=85)
with col2:
    st.title("Recipes Alternatives AI")

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
        
        with st.spinner("Saving your recipe..."):
            # In standalone mode, we just save to session state
            st.session_state.recipe_data = recipe_payload
            st.session_state.recipe_id = 1 # Dummy ID for compatibility
            st.success(f"Recipe '{title}' saved!")

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
                # Prepare Prompt (Logic moved from main.py)
                target = st.session_state.recipe_data
                prompt = (
                    f"You are a cooking assistant. Convert this recipe into a {transformation} version. "
                    f"Original: {target['title']}. Ingredients: {target['ingredients']}. Instructions: {target['instructions']}. "
                    "Return ONLY a JSON object with keys: 'title', 'ingredients' (list of strings), and 'instructions' (string)."
                )

                # Call Gemini directly
                response = client.models.generate_content(
                    model="gemini-2.0-flash-001",
                    contents=prompt,
                    config={"response_mime_type": "application/json"}
                )
                
                transformed_recipe_data = json.loads(response.text)
                
                # Display the new recipe
                st.success("Transformation complete!")
                st.subheader(f"✨ Transformed: {transformation} Version")
                with st.container(border=True, height=300):
                        st.markdown(parse_recipe_text(transformed_recipe_data))

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
