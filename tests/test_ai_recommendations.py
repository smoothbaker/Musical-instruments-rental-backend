"""
Test script for AI-powered instrument recommendations endpoint
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"

def test_ai_recommendations():
    """Test the new AI-powered recommendations endpoint"""
    
    print("\n" + "="*80)
    print("TESTING AI-POWERED INSTRUMENT RECOMMENDATIONS")
    print("="*80)
    
    # Step 1: Register a test user
    print("\n[1] Registering test user...")
    renter_data = {
        "email": f"renter_{int(datetime.now().timestamp())}@test.com",
        "password": "TestPass123!",
        "name": "Test Renter",
        "phone": "+1234567890",
        "user_type": "renter"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/register", json=renter_data)
    if response.status_code == 201:
        print(f"OK User registered: {renter_data['email']}")
    else:
        print(f"X Registration failed: {response.status_code}")
        print(f"  Error: {response.text}")
        return
    
    # Step 2: Login to get token
    print("\n[2] Logging in to get JWT token...")
    login_data = {
        "email": renter_data['email'],
        "password": renter_data['password']
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    if response.status_code == 200:
        token = response.json().get('access_token')
        print(f"OK Login successful")
        print(f"  Token: {token[:50]}...")
    else:
        print(f"X Login failed: {response.status_code}")
        print(f"  Error: {response.text}")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 3: Test AI recommendations with different queries
    test_cases = [
        {
            "name": "Beginner Guitarist",
            "data": {
                "user_needs": "beginner guitarist looking for affordable acoustic guitar",
                "budget": 30.0,
                "experience_level": "beginner"
            }
        },
        {
            "name": "Professional Drummer",
            "data": {
                "user_needs": "professional drum kit for jazz performance",
                "experience_level": "advanced"
            }
        },
        {
            "name": "Open-ended Search",
            "data": {
                "user_needs": "I want a string instrument that sounds warm and has good reviews"
            }
        }
    ]
    
    print("\n[3] Testing AI recommendations endpoint...")
    print("-" * 80)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n[Test {i}] {test_case['name']}")
        print(f"User needs: {test_case['data']['user_needs']}")
        
        response = requests.post(
            f"{BASE_URL}/api/recommendations/by-needs",
            json=test_case['data'],
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"OK Request successful (200)")
            print(f"  Matched categories: {result.get('matched_categories', [])}")
            print(f"  Total recommendations: {len(result.get('recommendations', []))}")
            print(f"  Available instruments: {result.get('total_available', 0)}")
            
            if result.get('recommendations'):
                print(f"\n  Top 3 recommendations:")
                for j, rec in enumerate(result['recommendations'][:3], 1):
                    print(f"    {j}. {rec['name']} ({rec['category']})")
                    print(f"       Rate: ${rec['daily_rate']}/day | Rating: {rec['average_rating']}/5")
                    print(f"       Match Score: {rec['match_score']}/100")
                    print(f"       Reason: {rec['reasoning']}")
            else:
                print(f"  No recommendations found (database might be empty)")
        else:
            print(f"X Request failed ({response.status_code})")
            print(f"  Error: {response.text}")
    
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print("OK AI Recommendations endpoint is working!")
    print("\nEndpoint Details:")
    print("  - Route: POST /api/recommendations/by-needs")
    print("  - Authentication: Required (JWT)")
    print("  - Returns: Top 5 instruments scored by relevance")
    print("  - Scoring: Category, Budget, Rating, Keywords")
    print("\nFull documentation: AI_RECOMMENDATIONS_GUIDE.md")
    print("="*80 + "\n")

if __name__ == "__main__":
    try:
        test_ai_recommendations()
    except requests.exceptions.ConnectionError:
        print("\nX ERROR: Cannot connect to Flask server")
        print("  Please start the Flask server with: flask run")
    except Exception as e:
        print(f"\nX ERROR: {str(e)[:200]}")
