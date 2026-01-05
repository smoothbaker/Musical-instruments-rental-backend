import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import create_app, db

app = create_app()
with app.app_context():
    db.create_all()
    client = app.test_client()

    print("=" * 60)
    print("COMPREHENSIVE API TEST SUITE")
    print("=" * 60)
    
    # Test 1: Register Owner
    print("\n[TEST 1] Register Instrument Owner")
    resp = client.post('/api/auth/register', json={
        'email': 'owner@test.com',
        'password': 'password123',
        'name': 'John Owner',
        'user_type': 'owner'
    })
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.get_data(as_text=True)[:100]}")
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}"
    owner_id = resp.get_json()['id']
    print(f"✓ Owner created with ID: {owner_id}")
    
    # Test 2: Register Renter
    print("\n[TEST 2] Register Renter User")
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
    
    # Test 3: Login as Owner
    print("\n[TEST 3] Login as Owner")
    resp = client.post('/api/auth/login', json={
        'email': 'owner@test.com',
        'password': 'password123'
    })
    print(f"Status: {resp.status_code}")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    owner_token = resp.get_json()['access_token']
    owner_user_data = resp.get_json()['user']
    assert owner_user_data['user_type'] == 'owner', "User type should be 'owner'"
    print(f"✓ Owner logged in successfully")
    
    # Test 4: Get Owner Profile
    print("\n[TEST 4] Get Owner Profile")
    resp = client.get('/api/auth/profile', headers={'Authorization': f'Bearer {owner_token}'})
    print(f"Status: {resp.status_code}")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    profile = resp.get_json()
    print(f"Profile: {profile}")
    assert profile['user_type'] == 'owner', "User type mismatch"
    print(f"✓ Profile retrieved successfully")
    
    # Test 5: Login as Renter
    print("\n[TEST 5] Login as Renter")
    resp = client.post('/api/auth/login', json={
        'email': 'renter@test.com',
        'password': 'password123'
    })
    print(f"Status: {resp.status_code}")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    renter_token = resp.get_json()['access_token']
    renter_user_data = resp.get_json()['user']
    assert renter_user_data['user_type'] == 'renter', "User type should be 'renter'"
    print(f"✓ Renter logged in successfully")
    
    # Test 6: Create Instrument as Owner
    print("\n[TEST 6] Create Instrument as Owner")
    resp = client.post('/api/instruments', json={
        'name': 'Electric Guitar',
        'category': 'guitar',
        'brand': 'Fender',
        'model': 'Stratocaster',
        'condition': 'excellent',
        'daily_rate': 25.0,
        'description': 'Premium electric guitar in excellent condition',
        'location': 'New York'
    }, headers={'Authorization': f'Bearer {owner_token}'})
    print(f"Status: {resp.status_code}")
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}"
    instrument_id = resp.get_json()['id']
    print(f"✓ Instrument created with ID: {instrument_id}")
    
    # Test 7: List Instruments (public)
    print("\n[TEST 7] List Instruments (Public)")
    resp = client.get('/api/instruments')
    print(f"Status: {resp.status_code}")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    instruments = resp.get_json()
    print(f"Found {len(instruments)} instruments")
    assert len(instruments) > 0, "Should have at least one instrument"
    print(f"✓ Instruments listed successfully")
    
    # Test 8: Get Instrument Details
    print("\n[TEST 8] Get Instrument Details")
    resp = client.get(f'/api/instruments/{instrument_id}')
    print(f"Status: {resp.status_code}")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    instrument = resp.get_json()
    print(f"Instrument: {instrument['name']} - ${instrument['daily_rate']}/day")
    print(f"✓ Instrument details retrieved")
    
    # Test 9: Create Rental as Renter
    print("\n[TEST 9] Create Rental as Renter")
    resp = client.post('/api/rentals', json={
        'instrument_id': instrument_id,
        'start_date': '2026-01-10',
        'end_date': '2026-01-15'
    }, headers={'Authorization': f'Bearer {renter_token}'})
    print(f"Status: {resp.status_code}")
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}"
    rental_id = resp.get_json()['rental_id']
    total_cost = resp.get_json()['total_cost']
    print(f"✓ Rental created with ID: {rental_id}, Total Cost: ${total_cost}")
    
    # Test 10: Get User Rentals
    print("\n[TEST 10] Get User Rentals")
    resp = client.get('/api/rentals', headers={'Authorization': f'Bearer {renter_token}'})
    print(f"Status: {resp.status_code}")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    rentals = resp.get_json()
    print(f"Found {len(rentals)} rentals for user")
    assert len(rentals) > 0, "Should have at least one rental"
    print(f"✓ Rentals retrieved successfully")
    
    # Test 11: Get Rental Details
    print("\n[TEST 11] Get Rental Details")
    resp = client.get(f'/api/rentals/{rental_id}', headers={'Authorization': f'Bearer {renter_token}'})
    print(f"Status: {resp.status_code}")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    rental = resp.get_json()
    print(f"Rental Status: {rental['status']}")
    print(f"✓ Rental details retrieved")
    
    # Test 12: Return Rental
    print("\n[TEST 12] Return Rental")
    resp = client.post(f'/api/rentals/{rental_id}/return', headers={'Authorization': f'Bearer {renter_token}'})
    print(f"Status: {resp.status_code}")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    print(f"✓ Rental returned successfully")
    
    # Test 13: List Users (CRUD)
    print("\n[TEST 13] List All Users")
    resp = client.get('/api/users', headers={'Authorization': f'Bearer {owner_token}'})
    print(f"Status: {resp.status_code}")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    users = resp.get_json()
    print(f"Found {len(users)} users")
    print(f"✓ Users listed successfully")
    
    # Test 14: Get Specific User
    print("\n[TEST 14] Get Specific User")
    resp = client.get(f'/api/users/{owner_id}', headers={'Authorization': f'Bearer {owner_token}'})
    print(f"Status: {resp.status_code}")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    user = resp.get_json()
    print(f"User: {user['name']} ({user['user_type']})")
    print(f"✓ User retrieved successfully")
    
    # Test 15: Update User (PUT)
    print("\n[TEST 15] Update User")
    resp = client.put(f'/api/users/{renter_id}', json={
        'name': 'Jane Updated Renter',
        'phone': '+1-555-0123'
    }, headers={'Authorization': f'Bearer {renter_token}'})
    print(f"Status: {resp.status_code}")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    updated_user = resp.get_json()
    print(f"Updated: {updated_user['name']}, Phone: {updated_user['phone']}")
    print(f"✓ User updated successfully")
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED! ✓")
    print("=" * 60)
