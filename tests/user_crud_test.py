import requests

BASE = 'http://127.0.0.1:5000'

# 1) Register an owner
r = requests.post(BASE + '/api/auth/register', json={
    'email': 'owner@example.com',
    'password': 'password123',
    'name': 'Owner User',
    'user_type': 'owner'
})
print('register owner', r.status_code, r.text)

# 2) Register a renter
r = requests.post(BASE + '/api/auth/register', json={
    'email': 'renter@example.com',
    'password': 'password123',
    'name': 'Renter User',
    'user_type': 'renter'
})
print('register renter', r.status_code, r.text)

# 3) Login as owner
r = requests.post(BASE + '/api/auth/login', json={
    'email': 'owner@example.com',
    'password': 'password123'
})
print('login owner', r.status_code)
if r.status_code == 200:
    tokens = r.json()
    access = tokens['access_token']
    headers = {'Authorization': f'Bearer {access}'}

    # 4) List users
    r = requests.get(BASE + '/api/users', headers=headers)
    print('list users', r.status_code, r.text)

    # 5) Get specific user
    r = requests.get(BASE + '/api/users/1', headers=headers)
    print('get user 1', r.status_code, r.text)

    # 6) Update user
    r = requests.put(BASE + '/api/users/1', json={
        'name': 'Updated Owner'
    }, headers=headers)
    print('update user', r.status_code, r.text)

print("Test completed. Check Swagger UI at http://127.0.0.1:5000/swagger-ui for interactive testing.")