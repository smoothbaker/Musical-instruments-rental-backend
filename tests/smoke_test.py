import requests

BASE = 'http://127.0.0.1:5000'

# 1) Register
r = requests.post(BASE + '/api/auth/register', json={
    'email': 'tester@example.com',
    'password': 'password123',
    'name': 'Tester'
})
print('register', r.status_code, r.text)

# 2) Login
r = requests.post(BASE + '/api/auth/login', json={
    'email': 'tester@example.com',
    'password': 'password123'
})
print('login', r.status_code, r.text)
if r.status_code != 200:
    raise SystemExit('login failed')

tokens = r.json()
access = tokens['access_token']
headers = {'Authorization': f'Bearer {access}'}

# 3) Create instrument
r = requests.post(BASE + '/api/instruments', json={
    'name': 'Test Guitar',
    'category': 'guitar',
    'daily_rate': 10.0
}, headers=headers)
print('create_instrument', r.status_code, r.text)

# 4) List instruments
r = requests.get(BASE + '/api/instruments')
print('list_instruments', r.status_code, r.text)

# 5) Create rental (use instrument id from create response)
if r.status_code == 200 and len(r.json())>0:
    inst = r.json()[0]
    instrument_id = inst['id']
    r2 = requests.post(BASE + '/api/rentals', json={
        'instrument_id': instrument_id,
        'start_date': '2026-01-05',
        'end_date': '2026-01-07'
    }, headers=headers)
    print('create_rental', r2.status_code, r2.text)
else:
    print('No instruments to rent')
