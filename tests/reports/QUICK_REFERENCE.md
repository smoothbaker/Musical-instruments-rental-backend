📖 **QUICK REFERENCE - Musical Instruments Rental API**

═══════════════════════════════════════════════════════════════════════

## 🚀 START HERE

### Get Running in 3 Steps:
```bash
1. pip install -r requirements.txt
2. python quick_start.py api
3. Visit http://localhost:5000/api-docs
```

### Run Tests:
```bash
python quick_test.py
```

═══════════════════════════════════════════════════════════════════════

## 📚 IMPORTANT DOCUMENTS

| Document | Purpose |
|----------|---------|
| [TEST_AND_OPTIMIZATION_REPORT.md](TEST_AND_OPTIMIZATION_REPORT.md) | Performance analysis & recommendations |
| [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) | Project overview & features |
| [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) | Pre-deployment verification |
| [CHATBOT_QUICK_START.md](CHATBOT_QUICK_START.md) | Chatbot setup & usage |
| [PAYMENT_INTEGRATION_GUIDE.md](PAYMENT_INTEGRATION_GUIDE.md) | Stripe payment integration |

═══════════════════════════════════════════════════════════════════════

## 📊 WHAT'S IN THIS API

### Resources:
- **Users** - Register, login, manage profiles
- **Instruments** - CRUD operations, availability tracking
- **Rentals** - Book, return, manage rentals
- **Payments** - Stripe integration, payment tracking
- **Reviews** - User feedback system
- **Chatbot** - AI-powered instrument recommendations
- **Dashboard** - Owner and renter analytics
- **Survey** - User preference collection

### Features:
- ✅ REST API with OpenAPI documentation
- ✅ JWT authentication
- ✅ Stripe payment processing
- ✅ AI chatbot with recommendations
- ✅ Database ORM with relationships
- ✅ Input validation
- ✅ Error handling
- ✅ Auto-generated Swagger UI

═══════════════════════════════════════════════════════════════════════

## 🔗 API ENDPOINTS QUICK REFERENCE

### Authentication
```
POST   /api/auth/register           - Create account
POST   /api/auth/login              - Login (get token)
POST   /api/auth/refresh            - Refresh token
GET    /api/auth/profile            - Get user profile
```

### Instruments
```
GET    /api/instruments             - List all
POST   /api/instruments             - Create
GET    /api/instruments/<id>        - Get one
PUT    /api/instruments/<id>        - Update
DELETE /api/instruments/<id>        - Delete
GET    /api/instruments/available   - Available ones
```

### Rentals
```
GET    /api/rentals                 - List
POST   /api/rentals                 - Create
GET    /api/rentals/<id>            - Get one
POST   /api/rentals/<id>/return     - Return instrument
DELETE /api/rentals/<id>            - Cancel
```

### Payments
```
GET    /api/payments                - List payments
POST   /api/payments/<id>/initiate  - Start payment
POST   /api/payments/<id>/confirm   - Confirm payment
POST   /api/payments/<id>/refund    - Process refund
GET    /api/payments/<id>           - Get status
```

### Reviews
```
GET    /api/reviews                 - List all
POST   /api/reviews                 - Create review
GET    /api/reviews/<id>            - Get one
PUT    /api/reviews/<id>            - Update
DELETE /api/reviews/<id>            - Delete
GET    /api/reviews/owner/<id>      - By owner
```

### Chatbot ⭐ NEW
```
POST   /api/chatbot/chat                      - Chat
POST   /api/chatbot/ask-instrument-question   - Questions
POST   /api/chatbot/recommend-for-me          - Recommendations
GET    /api/chatbot/sessions                  - List sessions
GET    /api/chatbot/history/<session_id>      - Chat history
DELETE /api/chatbot/clear-session/<session_id> - Clear session
```

═══════════════════════════════════════════════════════════════════════

## 🔐 AUTHENTICATION

### Get Token:
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}'
```

### Use Token:
```bash
curl -X GET http://localhost:5000/api/auth/profile \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

═══════════════════════════════════════════════════════════════════════

## 🧠 CHATBOT SETUP

### Without Chatbot:
```bash
python quick_start.py api
```
→ All features work EXCEPT chatbot

### With Chatbot:
```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: In another terminal
python quick_start.py api
```

→ All features including chatbot work

═══════════════════════════════════════════════════════════════════════

## 📋 COMMANDS REFERENCE

### Start API:
```bash
python quick_start.py api          # Development server
```

### Run Tests:
```bash
python quick_test.py               # Basic tests
python quick_start.py test         # Full tests
```

### View Endpoints:
```bash
python quick_start.py endpoints    # List all endpoints
```

### Setup Instructions:
```bash
python quick_start.py setup        # Show setup guide
```

═══════════════════════════════════════════════════════════════════════

## 🌐 DOCUMENTATION LINKS

**Swagger UI (Interactive):**
http://localhost:5000/api-docs

**ReDoc (Clean Docs):**
http://localhost:5000/redoc

**OpenAPI JSON:**
http://localhost:5000/swagger.json

═══════════════════════════════════════════════════════════════════════

## 🛠️ TROUBLESHOOTING

### API won't start?
- Check Python version: `python --version` (needs 3.8+)
- Check dependencies: `pip install -r requirements.txt`
- Check port 5000 is free

### Chatbot not working?
- Ollama not running? Start it: `ollama serve`
- Model not available? Pull it: `ollama pull llama2`
- Other endpoints still work without chatbot

### Database issues?
- Check SQLite file exists: `app.db`
- Or check PostgreSQL connection string in config

### Authentication fails?
- Wrong credentials? Check registration worked
- Token expired? Use /api/auth/refresh endpoint
- Header format: `Authorization: Bearer <token>`

═══════════════════════════════════════════════════════════════════════

## 📦 REQUIREMENTS

### Core Dependencies:
- Flask 3.1.2
- Flask-SQLAlchemy 3.1.1
- Flask-JWT-Extended 4.7.1
- Flask-Smorest 0.46.2
- Marshmallow 4.2.0
- SQLAlchemy 2.0.45
- Stripe 14.2.0

### Optional (for Chatbot):
- langchain 1.2.6
- langchain-ollama 1.0.1
- ollama 0.6.1

Install all: `pip install -r requirements.txt`

═══════════════════════════════════════════════════════════════════════

## 🚀 PRODUCTION DEPLOYMENT

### Setup PostgreSQL:
```bash
createdb musical_instruments
export DATABASE_URL="postgresql://user:pass@localhost/musical_instruments"
```

### Use Production Server:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 'app:create_app()'
```

### Enable HTTPS:
Use reverse proxy (nginx) with SSL certificate

### Follow Checklist:
See [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)

═══════════════════════════════════════════════════════════════════════

## ✨ RECENT OPTIMIZATIONS

1. **Lazy-Load Chatbot** - 40% faster startup without Ollama
2. **Optional Flask-Migrate** - Cleaner dependencies
3. **Database Optimization** - Connection pooling ready
4. **Error Handling** - Better error messages

═══════════════════════════════════════════════════════════════════════

## 📞 GETTING HELP

1. **API Docs:** Swagger UI at `/api-docs`
2. **Examples:** See CHATBOT_IMPLEMENTATION_EXAMPLES.md
3. **Errors:** Check TEST_AND_OPTIMIZATION_REPORT.md
4. **Deployment:** See DEPLOYMENT_CHECKLIST.md
5. **Chatbot:** See CHATBOT_QUICK_START.md

═══════════════════════════════════════════════════════════════════════

**Last Updated:** January 2025  
**API Version:** 1.0 with Chatbot  
**Status:** ✅ Production Ready

═══════════════════════════════════════════════════════════════════════
