from app import create_app, db
from app.models import User
import json

app = create_app()
with app.app_context():
    db.create_all()
    client = app.test_client()

    # Try registration
    try:
        resp = client.post('/api/auth/register',
                          data=json.dumps({
                              'email': 'test@example.com',
                              'password': 'password123',
                              'name': 'Test User',
                              'user_type': 'renter'
                          }),
                          content_type='application/json')
        print('Register response:', resp.status_code, resp.get_data(as_text=True))
    except Exception as e:
        print('Register error:', e)