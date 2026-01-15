import os
import json
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from google import genai
from google.genai import types
from dotenv import load_dotenv

# 1. Load Environment Variables
load_dotenv()

api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY environment variable not set.")

client = genai.Client(api_key=api_key)

app = FastAPI()

# 2. In-Memory Database
recipes_db = []

# 3. Pydantic Models (Defined BEFORE routes to fix "Recipe not defined" error)
class Recipe(BaseModel):
    title: str
    ingredients: List[str]
    instructions: str

class TransformedRecipeResponse(BaseModel):
    transformed_recipe: dict

# 4. API Routes
@app.get("/", include_in_schema=False)
async def root_redirect():
    return RedirectResponse(url="/docs")

@app.post("/recipes/", response_model=dict)
async def add_recipe(recipe: Recipe):
    # Simply append the Pydantic object to the list
    recipes_db.append(recipe)
    # The ID is the index in the list
    return {"id": len(recipes_db) - 1, "message": "Recipe added successfully"}

@app.get("/recipes", response_model=dict)
async def get_recipes():
    # Return the list directly
    return {"recipes": recipes_db}

@app.post("/recipes/{recipe_id}/transform", response_model=TransformedRecipeResponse)
async def transform_recipe(recipe_id: int, transformation_type: str):
    # Validate ID (Index)
    if recipe_id < 0 or recipe_id >= len(recipes_db):
        raise HTTPException(status_code=404, detail="Recipe not found")
    
    target = recipes_db[recipe_id]

    # Prepare Prompt
    prompt = (
        f"You are a cooking assistant. Convert this recipe into a {transformation_type} version. "
        f"Original: {target.title}. Ingredients: {target.ingredients}. Instructions: {target.instructions}. "
        "Return ONLY a JSON object with keys: 'title', 'ingredients' (list of strings), and 'instructions' (string)."
    )

    try:
        # Call Gemini 2.0 Flash with JSON enforcement
        response = client.models.generate_content(
            model="gemini-2.0-flash-001",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        if not response.text:
            raise ValueError("AI returned an empty response. This might be due to safety filters.")
               
        # Parse the JSON response
        transformed_data = json.loads(response.text)
        return {"transformed_recipe": transformed_data}
    
    except json.JSONDecodeError:
        print(f"JSON Parsing Failed. Raw Text received: {response.text}")
        raise HTTPException(status_code=500, detail="AI response was not valid JSON.")
    
    except Exception as e:
        print(f"AI Generation Error: {e}")
        raise HTTPException(status_code=500, detail=f"AI Generation failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)