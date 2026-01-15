import requests
import json

BASE_URL = "http://localhost:8000"

def test_api_flow():
    print(f"Testing API at {BASE_URL}...\n")

    # 1. Check initial state (Should be empty)
    print("1. GET /recipes (Initial State)")
    response = requests.get(f"{BASE_URL}/recipes")
    if response.status_code == 200:
        print(f"   SUCCESS: {response.json()}")
    else:
        print(f"   FAILED: {response.status_code}")

    # 2. Add a dummy recipe
    print("\n2. POST /recipes/ (Adding data)")
    new_recipe = {
        "title": "Test Omelet",
        "ingredients": ["Eggs", "Cheese", "Butter"],
        "instructions": "Whisk eggs, melt butter, cook."
    }
    
    response = requests.post(f"{BASE_URL}/recipes/", json=new_recipe)
    if response.status_code == 200:
        print(f"   SUCCESS: {response.json()}")
    else:
        print(f"   FAILED: {response.status_code} - {response.text}")

    # 3. Check state again (Should have 1 item)
    print("\n3. GET /recipes (After Update)")
    response = requests.get(f"{BASE_URL}/recipes")
    data = response.json()
    
    if response.status_code == 200 and len(data["recipes"]) > 0:
        print(f"   SUCCESS: Retrieved {len(data['recipes'])} recipe(s)")
        print(f"   DATA: {data}")
    else:
        print(f"   FAILED: List is still empty or error occurred.")

if __name__ == "__main__":
    try:
        test_api_flow()
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to server. Is Docker running on port 8000?")
