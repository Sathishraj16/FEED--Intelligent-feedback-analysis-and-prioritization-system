"""Test the new AI Action Analyzer functionality"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_action_analyzer():
    """Test various feedback scenarios with the new /analyze_action endpoint"""
    
    test_cases = [
        {
            "name": "High Priority Bug",
            "data": {
                "text": "The app crashes every time I try to upload a file! This is urgent, all our customers are affected",
                "priority": 0.9,
                "urgency": 0.8,
                "sentiment": -0.7,
                "impact": 0.9,
                "tags": ["bug", "crash"]
            },
            "expected_team": "Engineering (Core App Team)",
            "expected_action_contains": ["P1", "Critical", "reproduce"]
        },
        {
            "name": "Performance Issue",
            "data": {
                "text": "The app is really slow when loading the dashboard",
                "priority": 0.6,
                "urgency": 0.5,
                "sentiment": -0.3,
                "impact": 0.6,
                "tags": ["performance"]
            },
            "expected_team": "Engineering (Performance Team)",
            "expected_action_contains": ["database", "caching"]
        },
        {
            "name": "Feature Request",
            "data": {
                "text": "Would love to see a dark mode feature added to the app",
                "priority": 0.3,
                "urgency": 0.2,
                "sentiment": 0.5,
                "impact": 0.4,
                "tags": ["feature_request"]
            },
            "expected_team": "Product Management",
            "expected_action_contains": ["Product Backlog", "interview"]
        },
        {
            "name": "UI/Frontend Issue",
            "data": {
                "text": "The submit button doesn't work on the contact form",
                "priority": 0.7,
                "urgency": 0.6,
                "sentiment": -0.4,
                "impact": 0.5,
                "tags": ["bug"]
            },
            "expected_team": "Engineering (Frontend Team)",
            "expected_action_contains": ["logs", "sprint"]
        },
        {
            "name": "Billing Issue",
            "data": {
                "text": "I was charged twice for my subscription this month",
                "priority": 0.8,
                "urgency": 0.7,
                "sentiment": -0.6,
                "impact": 0.6,
                "tags": ["billing"]
            },
            "expected_team": "Finance/Billing Team",
            "expected_action_contains": ["billing", "contact"]
        },
        {
            "name": "UX Design Issue",
            "data": {
                "text": "The color scheme is hard to read and looks unprofessional",
                "priority": 0.4,
                "urgency": 0.3,
                "sentiment": -0.2,
                "impact": 0.3,
                "tags": ["design"]
            },
            "expected_team": "UX Design",
            "expected_action_contains": ["documentation", "design"]
        }
    ]
    
    print("🔍 Testing AI Action Analyzer")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n[Test {i}] {test_case['name']}")
        print(f"Input: {test_case['data']['text'][:50]}...")
        
        try:
            response = requests.post(
                f"{BASE_URL}/analyze_action",
                json=test_case['data'],
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                next_step = result.get("next_step", "")
                responsible_team = result.get("responsible_team", "")
                
                print(f"✓ Status: {response.status_code}")
                print(f"  Next Step: {next_step}")
                print(f"  Team: {responsible_team}")
                
                # Validate results
                team_match = responsible_team == test_case["expected_team"]
                action_match = any(keyword.lower() in next_step.lower() 
                                 for keyword in test_case["expected_action_contains"])
                
                if team_match:
                    print(f"  ✅ Team assignment correct")
                else:
                    print(f"  ❌ Team mismatch. Expected: {test_case['expected_team']}")
                
                if action_match:
                    print(f"  ✅ Action contains expected keywords")
                else:
                    print(f"  ❌ Action missing keywords: {test_case['expected_action_contains']}")
                    
            else:
                print(f"✗ Status: {response.status_code}")
                print(f"  Error: {response.text}")
                
        except Exception as e:
            print(f"✗ Request failed: {e}")
    
    print(f"\n{'=' * 60}")
    print("🎯 Test Summary:")
    print("- All tests should return 200 OK")
    print("- Teams should match expected assignments")
    print("- Actions should be specific and actionable")
    print("- Next steps should be under 80 characters")

if __name__ == "__main__":
    test_action_analyzer()
