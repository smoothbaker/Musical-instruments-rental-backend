# Musical Instruments Rental API

A Flask-based API for renting musical instruments.

## Features

- User registration and authentication (JWT)
- Instrument management (CRUD)
- Rental system
- Recommendations based on user history
- Reviews for instruments

## Setup

1. Clone the repository.

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Run the application:
   ```bash
   python run.py
   ```

The API will be available at `http://127.0.0.1:5000`.

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/profile` - Get user profile

### Instruments
- `GET /api/instruments` - List instruments (with filters)
- `GET /api/instruments/<id>` - Get instrument details
- `POST /api/instruments` - Create instrument (requires auth)

### Rentals
- `POST /api/rentals` - Create rental (requires auth)
- `GET /api/rentals` - Get user's rentals (requires auth)
- `GET /api/rentals/<id>` - Get rental details (requires auth)
- `POST /api/rentals/<id>/return` - Return rental (requires auth)

### Recommendations
- `GET /api/recommendations` - Get personalized recommendations (requires auth)

## Database

Uses SQLite by default (`music_rental.db` in `instance/` folder). Change in `app/config.py` for production.

## Testing

Run smoke tests:
```bash
python tests/client_smoke_test.py
```

## License

MIT