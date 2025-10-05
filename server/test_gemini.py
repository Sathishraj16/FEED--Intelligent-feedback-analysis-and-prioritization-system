"""Quick test to verify Gemini model name works"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
print(f"API Key loaded: {GEMINI_API_KEY[:10]}..." if GEMINI_API_KEY else "NO API KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    
    # Test with gemini-2.0-flash-exp
    try:
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        response = model.generate_content("Say hello in one word")
        print(f"✓ gemini-2.0-flash-exp works! Response: {response.text}")
    except Exception as e:
        print(f"✗ gemini-2.0-flash-exp failed: {e}")
    
    # List available models
    print("\nAvailable models:")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"  - {m.name}")
