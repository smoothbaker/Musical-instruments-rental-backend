import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import create_app, db
import json

app = create_app()
with app.app_context():
    # Reset database for clean test
    db.drop_all()
    db.create_all()
    client = app.test_client()

    print("=" * 60)
    print("SURVEY FEATURE TEST SUITE")
    print("=" * 60)

    # Test 1: Register a renter user
    print("\n[TEST 1] Register Renter User")
    resp = client.post('/api/auth/register', json={
        'email': 'renter@test.com',
        'password': 'password123',
        'name': 'Jane Renter',
        'user_type': 'renter'
    })
    print(f"Status: {resp.status_code}")
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}"
    renter_id = resp.get_json()['id']
    print(f"✓ Renter created with ID: {renter_id}")

    # Test 2: Login as renter
    print("\n[TEST 2] Login as Renter")
    resp = client.post('/api/auth/login', json={
        'email': 'renter@test.com',
        'password': 'password123'
    })
    print(f"Status: {resp.status_code}")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    renter_token = resp.get_json()['access_token']
    print(f"✓ Renter logged in successfully")

    # Test 3: Submit survey response
    print("\n[TEST 3] Submit Survey Response")
    resp = client.post('/api/survey', json={
        'preferred_instruments': 'guitar,piano,violin',
        'experience_level': 'intermediate',
        'favorite_genres': 'rock,jazz,classical',
        'budget_range': '50-100',
        'rental_frequency': 'monthly',
        'use_case': 'hobby and learning',
        'location': 'New York',
        'additional_notes': 'Looking for quality instruments for weekend jamming sessions'
    }, headers={'Authorization': f'Bearer {renter_token}'})
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.get_json()}")
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}"
    survey_id = resp.get_json()['id']
    print(f"✓ Survey response submitted with ID: {survey_id}")

    # Test 4: Get survey response
    print("\n[TEST 4] Get Survey Response")
    resp = client.get('/api/survey', headers={'Authorization': f'Bearer {renter_token}'})
    print(f"Status: {resp.status_code}")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    survey = resp.get_json()
    print(f"Survey Data:")
    print(f"  - Preferred Instruments: {survey['preferred_instruments']}")
    print(f"  - Experience Level: {survey['experience_level']}")
    print(f"  - Favorite Genres: {survey['favorite_genres']}")
    print(f"  - Budget Range: {survey['budget_range']}")
    print(f"  - Rental Frequency: {survey['rental_frequency']}")
    print(f"✓ Survey response retrieved successfully")

    # Test 5: Get survey by ID
    print("\n[TEST 5] Get Survey by ID")
    resp = client.get(f'/api/survey/{survey_id}', headers={'Authorization': f'Bearer {renter_token}'})
    print(f"Status: {resp.status_code}")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    print(f"✓ Survey retrieved by ID successfully")

    # Test 6: Update survey response
    print("\n[TEST 6] Update Survey Response")
    resp = client.put(f'/api/survey/{survey_id}', json={
        'experience_level': 'advanced',
        'budget_range': '100+',
        'rental_frequency': 'weekly'
    }, headers={'Authorization': f'Bearer {renter_token}'})
    print(f"Status: {resp.status_code}")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    updated_survey = resp.get_json()
    print(f"Updated Survey:")
    print(f"  - Experience Level: {updated_survey['experience_level']}")
    print(f"  - Budget Range: {updated_survey['budget_range']}")
    print(f"  - Rental Frequency: {updated_survey['rental_frequency']}")
    print(f"✓ Survey response updated successfully")

    # Test 7: Try to submit survey twice (should fail)
    print("\n[TEST 7] Try to Submit Survey Twice (Should Fail)")
    resp = client.post('/api/survey', json={
        'preferred_instruments': 'drums,bass',
        'experience_level': 'beginner',
        'favorite_genres': 'rock',
        'budget_range': '0-25',
        'rental_frequency': 'rarely',
        'use_case': 'learning',
        'location': 'Boston'
    }, headers={'Authorization': f'Bearer {renter_token}'})
    print(f"Status: {resp.status_code}")
    assert resp.status_code == 400, f"Expected 400, got {resp.status_code}"
    print(f"✓ Correctly prevented duplicate survey submission")

    # Test 8: Register an owner and try to submit survey (should fail)
    print("\n[TEST 8] Owner Tries to Submit Survey (Should Fail)")
    resp = client.post('/api/auth/register', json={
        'email': 'owner@test.com',
        'password': 'password123',
        'name': 'John Owner',
        'user_type': 'owner'
    })
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}"
    
    resp = client.post('/api/auth/login', json={
        'email': 'owner@test.com',
        'password': 'password123'
    })
    owner_token = resp.get_json()['access_token']

    resp = client.post('/api/survey', json={
        'preferred_instruments': 'guitar',
        'experience_level': 'advanced',
        'favorite_genres': 'rock',
        'budget_range': '100+',
        'rental_frequency': 'frequently',
        'use_case': 'professional',
        'location': 'Los Angeles'
    }, headers={'Authorization': f'Bearer {owner_token}'})
    print(f"Status: {resp.status_code}")
    assert resp.status_code == 403, f"Expected 403, got {resp.status_code}"
    print(f"✓ Correctly prevented owner from submitting survey")

    # Test 9: Delete survey response
    print("\n[TEST 9] Delete Survey Response")
    resp = client.delete(f'/api/survey/{survey_id}', headers={'Authorization': f'Bearer {renter_token}'})
    print(f"Status: {resp.status_code}")
    assert resp.status_code == 204, f"Expected 204, got {resp.status_code}"
    print(f"✓ Survey response deleted successfully")

    # Test 10: Try to get deleted survey (should fail)
    print("\n[TEST 10] Get Deleted Survey (Should Fail)")
    resp = client.get(f'/api/survey/{survey_id}', headers={'Authorization': f'Bearer {renter_token}'})
    print(f"Status: {resp.status_code}")
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}"
    print(f"✓ Correctly returned 404 for deleted survey")

    print("\n" + "=" * 60)
    print("ALL SURVEY TESTS PASSED! ✓")
    print("=" * 60)
