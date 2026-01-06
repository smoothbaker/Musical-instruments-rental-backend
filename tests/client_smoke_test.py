import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import create_app, db
import json

app = create_app()
with app.app_context():
    db.create_all()
    client = app.test_client()

    # Register owner
    resp = client.post('/api/auth/register', json={
        'email': 'owner@example.com',
        'password': 'password123',
        'name': 'Owner',
        'user_type': 'owner'
    })
    print('register_owner', resp.status_code, resp.get_data(as_text=True))

    # Login as owner
    resp = client.post('/api/auth/login', json={
        'email': 'owner@example.com',
        'password': 'password123'
    })
    print('login_owner', resp.status_code, resp.get_data(as_text=True))
    if resp.status_code != 200:
        raise SystemExit('owner login failed')

    owner_tokens = resp.get_json()
    owner_access = owner_tokens['access_token']
    owner_headers = {'Authorization': f'Bearer {owner_access}'}

    # Create instrument (catalog)
    resp = client.post('/api/instruments', json={
        'name': 'Test Guitar',
        'category': 'guitar',
        'brand': 'Fender',
        'model': 'Stratocaster',
        'description': 'A great guitar'
    }, headers=owner_headers)
    print('create_instrument', resp.status_code, resp.get_data(as_text=True))

    # Create instru_ownership
    resp = client.post('/api/instru-ownership', json={
        'instrument_id': 1,
        'condition': 'new',
        'daily_rate': 15.0,
        'location': 'New York'
    }, headers=owner_headers)
    print('create_instru_ownership', resp.status_code, resp.get_data(as_text=True))

    # Register renter
    resp = client.post('/api/auth/register', json={
        'email': 'renter@example.com',
        'password': 'password123',
        'name': 'Renter',
        'user_type': 'renter'
    })
    print('register_renter', resp.status_code, resp.get_data(as_text=True))

    # Login as renter
    resp = client.post('/api/auth/login', json={
        'email': 'renter@example.com',
        'password': 'password123'
    })
    print('login_renter', resp.status_code, resp.get_data(as_text=True))
    if resp.status_code != 200:
        raise SystemExit('renter login failed')

    renter_tokens = resp.get_json()
    renter_access = renter_tokens['access_token']
    renter_headers = {'Authorization': f'Bearer {renter_access}'}

    # List available instru_ownership
    resp = client.get('/api/instru-ownership')
    print('list_instru_ownership', resp.status_code, resp.get_data(as_text=True))

    # Create rental
    resp = client.post('/api/rentals', json={
        'instru_ownership_id': 1,
        'start_date': '2026-01-05',
        'end_date': '2026-01-07'
    }, headers=renter_headers)
    print('create_rental', resp.status_code, resp.get_data(as_text=True))
