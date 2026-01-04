import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import create_app, db
import json

app = create_app()
with app.app_context():
    db.create_all()
    client = app.test_client()

    # Register
    resp = client.post('/api/auth/register', json={
        'email': 'tester2@example.com',
        'password': 'password123',
        'name': 'Tester2'
    })
    print('register', resp.status_code, resp.get_data(as_text=True))

    # Login
    resp = client.post('/api/auth/login', json={
        'email': 'tester2@example.com',
        'password': 'password123'
    })
    print('login', resp.status_code, resp.get_data(as_text=True))
    if resp.status_code != 200:
        raise SystemExit('login failed')

    tokens = resp.get_json()
    access = tokens['access_token']
    headers = {'Authorization': f'Bearer {access}'}

    # Create instrument
    resp = client.post('/api/instruments', json={
        'name': 'Client Guitar',
        'category': 'guitar',
        'daily_rate': 15.0
    }, headers=headers)
    print('create_instrument', resp.status_code, resp.get_data(as_text=True))

    # List instruments
    resp = client.get('/api/instruments')
    print('list_instruments', resp.status_code, resp.get_data(as_text=True))

    # Create rental
    instruments = resp.get_json()
    if instruments:
        instrument_id = instruments[0]['id']
        resp = client.post('/api/rentals', json={
            'instrument_id': instrument_id,
            'start_date': '2026-01-05',
            'end_date': '2026-01-07'
        }, headers=headers)
        print('create_rental', resp.status_code, resp.get_data(as_text=True))
    else:
        print('no instruments')
