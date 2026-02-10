"""
Quick script to list available Gemini models
"""
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

if not GEMINI_API_KEY:
    print("❌ GEMINI_API_KEY not set!")
    print("Please add it to your .env file")
    exit(1)

try:
    print("🔍 Listing available Gemini models...\n")
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    models = client.models.list()
    
    print(f"Found {len(list(models))} models:\n")
    
    for model in models:
        print(f"  📦 {model.name}")
        if hasattr(model, 'supported_generation_methods'):
            if model.supported_generation_methods:
                print(f"     Supports: {', '.join(model.supported_generation_methods)}")
        print()
    
    print("\n✅ Use one of these model names in your code!")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    print("\nIf you see 429 errors, you may have hit rate limits.")
    print("Wait a few minutes and try again.")
