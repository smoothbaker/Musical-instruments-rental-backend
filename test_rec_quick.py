"""Simple test for AI recommendations endpoint"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"

# Register
email = f"test_ai_{int(datetime.now().timestamp())}@test.com"
user_data = {
    "email": email,
    "password": "Test123!",
    "name": "AI Tester",
    "user_type": "renter"
}

r = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
print(f"1. Register: {r.status_code}")

# Login
login_data = {"email": email, "password": "Test123!"}
r = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
token = r.json()['access_token']
print(f"2. Login: {r.status_code}")

# Test AI Recommendations
headers = {"Authorization": f"Bearer {token}"}
rec_req = {
    "user_needs": "beginner guitarist looking for affordable acoustic guitar",
    "budget": 30.0
}

r = requests.post(f"{BASE_URL}/api/recommendations/by-needs", json=rec_req, headers=headers)
print(f"3. AI Recommendations: {r.status_code}")

if r.status_code == 200:
    result = r.json()
    print(f"\nSUCCESS!")
    print(f"  Categories matched: {result.get('matched_categories')}")
    print(f"  Found {len(result.get('recommendations', []))} recommendations")
    if result['recommendations']:
        top = result['recommendations'][0]
        print(f"\nTop recommendation:")
        print(f"  Name: {top['name']}")
        print(f"  Category: {top['category']}")
        print(f"  Daily Rate: ${top['daily_rate']}")
        print(f"  Rating: {top['average_rating']}/5")
        print(f"  Match Score: {top['match_score']}/100")
else:
    print(f"ERROR: {r.text}")
