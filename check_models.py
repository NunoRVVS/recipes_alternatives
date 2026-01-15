import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

# 1. Setup Client
api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("Error: API Key not found.")
    exit(1)

client = genai.Client(api_key=api_key)

print(f"Fetching models using key: {api_key[:5]}... (hidden)\n")

try:
    # 2. List all models simply
    print("--- AVAILABLE MODELS ---")
    for model in client.models.list():
        # We use getattr to safely get the display name, defaulting to "Unknown" if missing
        display_name = getattr(model, 'display_name', 'Unknown')
        print(f"ID: {model.name} | Name: {display_name}")
        
except Exception as e:
    print(f"\nError listing models: {e}")
