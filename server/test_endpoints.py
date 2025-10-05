"""
Test script to verify /suggest_reply and /summarize endpoints handle all edge cases.
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoint(name, url, test_cases):
    print(f"\n{'='*60}")
    print(f"Testing {name}")
    print(f"{'='*60}")
    
    for i, (description, body, headers) in enumerate(test_cases, 1):
        print(f"\n[Test {i}] {description}")
        print(f"  Body: {body}")
        
        try:
            response = requests.post(url, data=body, headers=headers, timeout=10)
            print(f"  ✓ Status: {response.status_code}")
            print(f"  Response: {response.text[:200]}")
        except Exception as e:
            print(f"  ✗ Error: {e}")

def main():
    # Test cases for /suggest_reply
    suggest_reply_tests = [
        ("Valid: feedback field", '{"feedback": "The feature is confusing"}', {"Content-Type": "application/json"}),
        ("Valid: text field", '{"text": "The feature is confusing"}', {"Content-Type": "application/json"}),
        ("Valid: feedback + sentiment + urgency", '{"feedback": "App crashes", "sentiment": -0.5, "urgency": 0.9}', {"Content-Type": "application/json"}),
        ("Invalid: empty JSON object", '{}', {"Content-Type": "application/json"}),
        ("Invalid: malformed JSON", 'not valid json', {"Content-Type": "application/json"}),
        ("Invalid: wrong field name", '{"message": "test"}', {"Content-Type": "application/json"}),
        ("Invalid: empty string", '', {"Content-Type": "application/json"}),
    ]
    
    # Test cases for /summarize
    summarize_tests = [
        ("Valid: text field", '{"text": "The app crashes when I save"}', {"Content-Type": "application/json"}),
        ("Valid: feedback field", '{"feedback": "The app crashes when I save"}', {"Content-Type": "application/json"}),
        ("Invalid: empty JSON object", '{}', {"Content-Type": "application/json"}),
        ("Invalid: malformed JSON", '{invalid}', {"Content-Type": "application/json"}),
        ("Invalid: wrong field name", '{"content": "test"}', {"Content-Type": "application/json"}),
    ]
    
    test_endpoint("/suggest_reply", f"{BASE_URL}/suggest_reply", suggest_reply_tests)
    test_endpoint("/summarize", f"{BASE_URL}/summarize", summarize_tests)
    
    print(f"\n{'='*60}")
    print("Testing Complete!")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
