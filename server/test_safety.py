"""Test Gemini safety settings"""
import os
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
print(f"✓ API Key loaded: {GEMINI_API_KEY[:20]}..." if GEMINI_API_KEY else "✗ NO API KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    
    # Test with proper safety settings
    safety_settings = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }
    
    print("\n=== Testing gemini-2.5-flash with BLOCK_NONE ===")
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        # Test 1: Simple feedback
        print("\n[Test 1] Simple feedback:")
        response = model.generate_content(
            "Summarize this feedback: The app crashes when I save my work",
            safety_settings=safety_settings
        )
        print(f"Response: {response.text}")
        print(f"Finish reason: {response.candidates[0].finish_reason if response.candidates else 'No candidates'}")
        
        # Test 2: Negative feedback
        print("\n[Test 2] Negative feedback:")
        response = model.generate_content(
            "Write a support reply for: This feature is terrible and frustrating",
            safety_settings=safety_settings
        )
        print(f"Response: {response.text}")
        print(f"Finish reason: {response.candidates[0].finish_reason if response.candidates else 'No candidates'}")
        
        # Test 3: Check what's actually being blocked
        print("\n[Test 3] Check safety ratings:")
        response = model.generate_content(
            "Summarize: Users are angry about the login issues",
            safety_settings=safety_settings
        )
        if response.candidates:
            print(f"Finish reason: {response.candidates[0].finish_reason}")
            print(f"Safety ratings: {response.candidates[0].safety_ratings}")
        print(f"Response: {response.text if hasattr(response, 'text') else 'No text'}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
