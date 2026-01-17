"""Test JWT token creation and verification"""

from app import create_app
import json

def test_jwt_flow():
    app = create_app()
    client = app.test_client()
    
    print("Testing JWT Token Flow\n" + "="*50)
    
    # Step 1: Register a user
    print("\n1. Registering a test user...")
    register_data = {
        'email': 'jwttest@example.com',
        'name': 'JWT Test User',
        'phone': '1234567890',
        'user_type': 'renter',
        'password': 'TestPassword123!'
    }
    
    response = client.post('/api/auth/register', 
                          json=register_data,
                          content_type='application/json')
    
    if response.status_code == 201:
        print(f"   ✓ User registered successfully (Status: {response.status_code})")
    else:
        print(f"   ✗ Registration failed (Status: {response.status_code})")
        print(f"   Response: {response.get_json()}")
        return
    
    # Step 2: Login to get token
    print("\n2. Logging in to get JWT token...")
    login_data = {
        'email': 'jwttest@example.com',
        'password': 'TestPassword123!'
    }
    
    response = client.post('/api/auth/login',
                          json=login_data,
                          content_type='application/json')
    
    if response.status_code == 200:
        data = response.get_json()
        access_token = data.get('access_token')
        print(f"   ✓ Login successful (Status: {response.status_code})")
        print(f"   Token: {access_token[:50]}...")
    else:
        print(f"   ✗ Login failed (Status: {response.status_code})")
        print(f"   Response: {response.get_json()}")
        return
    
    # Step 3: Use token to access protected endpoint
    print("\n3. Accessing /api/auth/profile with JWT token...")
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    response = client.get('/api/auth/profile',
                         headers=headers)
    
    if response.status_code == 200:
        data = response.get_json()
        print(f"   ✓ Profile access successful (Status: {response.status_code})")
        print(f"   User data: {json.dumps(data, indent=2)[:200]}...")
    else:
        print(f"   ✗ Profile access failed (Status: {response.status_code})")
        print(f"   Response: {response.get_json()}")
    
    print("\n" + "="*50)
    print("Test completed!")

if __name__ == '__main__':
    test_jwt_flow()
