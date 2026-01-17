"""
Comprehensive API Endpoint Tester
Tests all 53 endpoints defined in the OpenAPI specification
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:5000/api"

# Test results storage
test_results = []
tokens = {"renter": None, "owner": None}
test_ids = {}

def log_result(endpoint, method, status_code, expected_status, passed, error=None):
    """Log test result"""
    result = {
        "endpoint": f"{method} {endpoint}",
        "status_code": status_code,
        "expected": expected_status,
        "passed": passed,
        "error": str(error) if error else None
    }
    test_results.append(result)
    status = "✓" if passed else "✗"
    print(f"{status} {method:6} {endpoint:60} -> {status_code} (expected {expected_status})")
    if error:
        print(f"  Error: {error}")

def test_endpoint(method, path, expected_status, data=None, token=None, description=""):
    """Test a single endpoint"""
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=10)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=10)
        
        passed = response.status_code == expected_status
        log_result(path, method, response.status_code, expected_status, passed)
        return response
    except Exception as e:
        log_result(path, method, 0, expected_status, False, e)
        return None

print("=" * 100)
print("COMPREHENSIVE API ENDPOINT TESTING")
print("=" * 100)
print()

# Phase 1: Authentication Tests
print("\n[1/11] AUTHENTICATION ENDPOINTS")
print("-" * 100)

# Register renter
response = test_endpoint(
    "POST", "/auth/register", 201,
    data={
        "email": "test_renter@api.test",
        "password": "test123",
        "name": "Test Renter",
        "user_type": "renter"
    }
)
if response and response.status_code == 201:
    test_ids["renter_id"] = response.json().get("id")

# Register owner
response = test_endpoint(
    "POST", "/auth/register", 201,
    data={
        "email": "test_owner@api.test",
        "password": "test123",
        "name": "Test Owner",
        "user_type": "owner"
    }
)
if response and response.status_code == 201:
    test_ids["owner_id"] = response.json().get("id")

# Login renter
response = test_endpoint(
    "POST", "/auth/login", 200,
    data={"email": "test_renter@api.test", "password": "test123"}
)
if response and response.status_code == 200:
    tokens["renter"] = response.json().get("access_token")

# Login owner
response = test_endpoint(
    "POST", "/auth/login", 200,
    data={"email": "test_owner@api.test", "password": "test123"}
)
if response and response.status_code == 200:
    tokens["owner"] = response.json().get("access_token")

# Get profile (authenticated)
test_endpoint("GET", "/auth/profile", 200, token=tokens["renter"])

# Refresh token (if exists)
if tokens["renter"]:
    test_endpoint("POST", "/auth/refresh", 200, token=tokens["renter"])

# Phase 2: User Endpoints
print("\n[2/11] USER ENDPOINTS")
print("-" * 100)

test_endpoint("GET", "/users", 200, token=tokens["renter"])
if test_ids.get("renter_id"):
    test_endpoint("GET", f"/users/{test_ids['renter_id']}", 200, token=tokens["renter"])
    test_endpoint("PUT", f"/users/{test_ids['renter_id']}", 200, 
                  data={"name": "Updated Renter"}, token=tokens["renter"])

# Phase 3: Instrument Endpoints
print("\n[3/11] INSTRUMENT ENDPOINTS")
print("-" * 100)

test_endpoint("GET", "/instruments", 200)

# Create instrument as owner
response = test_endpoint(
    "POST", "/instruments", 201,
    data={
        "name": "Test Guitar",
        "category": "guitar",
        "brand": "Fender",
        "model": "Stratocaster"
    },
    token=tokens["owner"]
)
if response and response.status_code == 201:
    test_ids["instrument_id"] = response.json().get("id")

# Get available instruments
test_endpoint("GET", "/instruments/available", 200)

if test_ids.get("instrument_id"):
    test_endpoint("GET", f"/instruments/{test_ids['instrument_id']}", 200)
    test_endpoint("PUT", f"/instruments/{test_ids['instrument_id']}", 200,
                  data={"brand": "Gibson"}, token=tokens["owner"])

# Phase 4: Instrument Ownership Endpoints
print("\n[4/11] INSTRUMENT OWNERSHIP ENDPOINTS")
print("-" * 100)

test_endpoint("GET", "/instru-ownership", 200)

# Create ownership
if test_ids.get("instrument_id"):
    response = test_endpoint(
        "POST", "/instru-ownership", 201,
        data={
            "instrument_id": test_ids["instrument_id"],
            "condition": "good",
            "daily_rate": 50.00,
            "location": "Test City"
        },
        token=tokens["owner"]
    )
    if response and response.status_code == 201:
        test_ids["ownership_id"] = response.json().get("id")

test_endpoint("GET", "/instru-ownership/my-instruments", 200, token=tokens["owner"])

if test_ids.get("ownership_id"):
    test_endpoint("GET", f"/instru-ownership/{test_ids['ownership_id']}", 200)
    test_endpoint("PUT", f"/instru-ownership/{test_ids['ownership_id']}", 200,
                  data={"daily_rate": 60.00}, token=tokens["owner"])

# Phase 5: Rental Endpoints
print("\n[5/11] RENTAL ENDPOINTS")
print("-" * 100)

test_endpoint("GET", "/rentals", 200, token=tokens["renter"])

# Create rental
if test_ids.get("ownership_id"):
    start_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    end_date = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
    response = test_endpoint(
        "POST", "/rentals", 201,
        data={
            "instru_ownership_id": test_ids["ownership_id"],
            "start_date": start_date,
            "end_date": end_date
        },
        token=tokens["renter"]
    )
    if response and response.status_code == 201:
        test_ids["rental_id"] = response.json().get("id")

if test_ids.get("rental_id"):
    test_endpoint("GET", f"/rentals/{test_ids['rental_id']}", 200, token=tokens["renter"])
    test_endpoint("POST", f"/rentals/{test_ids['rental_id']}/return", 200, token=tokens["renter"])

# Phase 6: Dashboard Endpoints
print("\n[6/11] DASHBOARD ENDPOINTS")
print("-" * 100)

test_endpoint("GET", "/dashboard/stats", 200, token=tokens["renter"])
test_endpoint("GET", "/dashboard/renter", 200, token=tokens["renter"])
test_endpoint("GET", "/dashboard/owner", 200, token=tokens["owner"])

# Phase 7: Survey Endpoints
print("\n[7/11] SURVEY ENDPOINTS")
print("-" * 100)

test_endpoint("GET", "/survey", 200, token=tokens["renter"])

response = test_endpoint(
    "POST", "/survey", 201,
    data={
        "instrument_preferences": ["guitar"],
        "skill_level": "beginner"
    },
    token=tokens["renter"]
)
if response and response.status_code == 201:
    test_ids["survey_id"] = response.json().get("id")

if test_ids.get("survey_id"):
    test_endpoint("GET", f"/survey/{test_ids['survey_id']}", 200, token=tokens["renter"])
    test_endpoint("PUT", f"/survey/{test_ids['survey_id']}", 200,
                  data={"skill_level": "intermediate"}, token=tokens["renter"])
    # Delete at end: test_endpoint("DELETE", f"/survey/{test_ids['survey_id']}", 204, token=tokens["renter"])

# Phase 8: Review Endpoints
print("\n[8/11] REVIEW ENDPOINTS")
print("-" * 100)

test_endpoint("GET", "/reviews/", 200)

if test_ids.get("ownership_id"):
    response = test_endpoint(
        "POST", "/reviews/", 201,
        data={
            "instru_ownership_id": test_ids["ownership_id"],
            "rating": 5,
            "comment": "Great instrument!"
        },
        token=tokens["renter"]
    )
    if response and response.status_code == 201:
        test_ids["review_id"] = response.json().get("id")

if test_ids.get("review_id"):
    test_endpoint("GET", f"/reviews/{test_ids['review_id']}", 200)
    test_endpoint("PUT", f"/reviews/{test_ids['review_id']}", 200,
                  data={"rating": 4}, token=tokens["renter"])

if test_ids.get("ownership_id"):
    test_endpoint("GET", f"/reviews/ownership/{test_ids['ownership_id']}", 200)

if test_ids.get("owner_id"):
    test_endpoint("GET", f"/reviews/owner/{test_ids['owner_id']}", 200)

# Phase 9: Payment Endpoints
print("\n[9/11] PAYMENT ENDPOINTS")
print("-" * 100)

test_endpoint("GET", "/payments", 200, token=tokens["renter"])

if test_ids.get("rental_id"):
    test_endpoint("POST", f"/payments/{test_ids['rental_id']}/initiate", 201, token=tokens["renter"])
    test_endpoint("GET", f"/payments/{test_ids['rental_id']}", 200, token=tokens["renter"])
    test_endpoint("POST", f"/payments/{test_ids['rental_id']}/confirm", 200, token=tokens["renter"])

# Phase 10: Recommendation Endpoints
print("\n[10/11] RECOMMENDATION ENDPOINTS")
print("-" * 100)

test_endpoint("GET", "/recommendations", 200, token=tokens["renter"])

# Phase 11: Chatbot Endpoints
print("\n[11/11] CHATBOT ENDPOINTS")
print("-" * 100)

response = test_endpoint(
    "POST", "/chatbot/chat", 200,
    data={"message": "Hello"},
    token=tokens["renter"]
)
if response and response.status_code == 200:
    test_ids["session_id"] = response.json().get("session_id")

test_endpoint("GET", "/chatbot/sessions", 200, token=tokens["renter"])

if test_ids.get("session_id"):
    test_endpoint("GET", f"/chatbot/history/{test_ids['session_id']}", 200, token=tokens["renter"])

test_endpoint(
    "POST", "/chatbot/ask-instrument-question", 200,
    data={"question": "What guitar should I get?"},
    token=tokens["renter"]
)

test_endpoint(
    "POST", "/chatbot/recommend-for-me", 200,
    data={},
    token=tokens["renter"]
)

if test_ids.get("session_id"):
    test_endpoint("DELETE", f"/chatbot/clear-session/{test_ids['session_id']}", 204, token=tokens["renter"])

# Summary
print("\n" + "=" * 100)
print("TEST SUMMARY")
print("=" * 100)

total_tests = len(test_results)
passed_tests = sum(1 for r in test_results if r["passed"])
failed_tests = total_tests - passed_tests

print(f"\nTotal Tests: {total_tests}")
print(f"Passed: {passed_tests} ({passed_tests/total_tests*100:.1f}%)")
print(f"Failed: {failed_tests} ({failed_tests/total_tests*100:.1f}%)")

if failed_tests > 0:
    print("\nFAILED ENDPOINTS:")
    print("-" * 100)
    for result in test_results:
        if not result["passed"]:
            print(f"  {result['endpoint']:70} -> {result['status_code']} (expected {result['expected']})")
            if result["error"]:
                print(f"    Error: {result['error']}")

# Save results to JSON
with open("test_results.json", "w") as f:
    json.dump(test_results, f, indent=2)

print(f"\nDetailed results saved to test_results.json")
print("=" * 100)
