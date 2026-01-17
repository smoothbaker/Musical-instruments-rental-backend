# Swagger Quick Start Guide

## ✅ Swagger is Now Configured!

Your Musical Instruments Rental API now has **fully configured Swagger/OpenAPI documentation**.

## 🚀 Quick Start (3 Steps)

### Step 1: Start the API Server
```bash
python run.py
```

Expected output:
```
* Running on http://0.0.0.0:5000
* WARNING: This is a development server. Do not use in production.
```

### Step 2: Open Swagger UI in Browser
```
http://localhost:5000/swagger-ui
```

You'll see:
- ✅ Interactive API documentation
- ✅ All endpoints listed
- ✅ "Try it out" button on each endpoint
- ✅ "Authorize" button for authentication

### Step 3: Test an Endpoint
1. Find **POST /api/auth/register**
2. Click **"Try it out"**
3. Enter test data:
   ```json
   {
     "email": "test@example.com",
     "password": "password123",
     "name": "Test User",
     "user_type": "renter"
   }
   ```
4. Click **"Execute"**
5. See the response with your token!

---

## 📚 Available Documentation Views

| View | URL | Purpose |
|------|-----|---------|
| **Swagger UI** | http://localhost:5000/swagger-ui | Interactive testing |
| **ReDoc** | http://localhost:5000/redoc | Clean documentation |
| **OpenAPI JSON** | http://localhost:5000/swagger.json | Machine-readable spec |

---

## 🔑 Authentication Flow

### Get Your Token

1. **Register**
   - POST `/api/auth/register`
   - Body: `{"email": "your@email.com", "password": "password", "name": "Name", "user_type": "renter"}`
   - Response includes: `access_token`

2. **Copy the Token**
   - Look for `access_token` in response
   - Example: `eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...`

3. **Authorize in Swagger**
   - Click 🔒 **"Authorize"** button (top right)
   - Click **"Bearer"** option
   - Paste your token in the field
   - Click **"Authorize"**

4. **Now All Protected Endpoints Are Available**
   - All subsequent requests will include your token
   - Try any endpoint now!

---

## 🎯 What You Can Do in Swagger

### 1. **View API Documentation**
- Click any endpoint to expand it
- See description, parameters, and responses
- View example request/response

### 2. **Send Test Requests**
- Click **"Try it out"**
- Fill in request parameters
- Click **"Execute"**
- See live response

### 3. **Copy API Calls**
- Scroll down after executing
- Find **"Curl"** section
- Copy the curl command
- Use in your scripts/code

### 4. **Test Different Scenarios**
- Try success cases
- Try error cases (invalid data)
- Try authorization errors
- Test edge cases

### 5. **View Response Examples**
- Each endpoint shows example responses
- See all possible status codes (200, 400, 401, 404, etc.)
- Understand error messages

---

## 📊 Endpoints Overview

### Authentication (No Token Required)
```
POST /api/auth/register      - Create new account
POST /api/auth/login         - Login to existing account
POST /api/auth/refresh       - Get new access token
```

### User Management (Token Required)
```
GET  /api/users/profile      - Get your profile
PUT  /api/users/profile      - Update your profile
GET  /api/users/{id}         - Get another user's info
```

### Instruments (View without token, Create with token)
```
GET  /api/instruments                    - List all
POST /api/instruments                    - Create new
GET  /api/instruments/{id}              - Get details
PUT  /api/instruments/{id}              - Update
DELETE /api/instruments/{id}            - Delete
```

### Rentals (Requires Token)
```
GET  /api/rentals                        - List your rentals
POST /api/rentals                        - Create rental request
GET  /api/rentals/{id}                  - Get rental details
DELETE /api/rentals/{id}                - Cancel rental
```

### Payments (Requires Token)
```
POST /api/payments/{rental_id}/initiate  - Start payment
POST /api/payments/{rental_id}/confirm   - Confirm payment
GET  /api/payments                       - List payments
POST /api/payments/{id}/refund          - Refund payment
```

### Surveys (Requires Token)
```
GET  /api/survey                         - Get your survey
POST /api/survey                         - Create survey
PUT  /api/survey/{id}                   - Update survey
DELETE /api/survey/{id}                 - Delete survey
```

### More Endpoints
- Reviews, Recommendations, Dashboard
- Check Swagger UI for complete list!

---

## 🧪 Example Testing Workflow

### Step 1: Register
```
1. Click: POST /api/auth/register
2. Try it out
3. Enter:
   {
     "email": "alice@example.com",
     "password": "secure_password",
     "name": "Alice",
     "user_type": "renter"
   }
4. Execute
5. Copy access_token from response
```

### Step 2: Authorize
```
1. Click Authorize (lock icon)
2. Click Bearer option
3. Paste your token
4. Click Authorize
```

### Step 3: View Profile
```
1. Click: GET /api/users/profile
2. Try it out
3. Execute
4. See your user profile!
```

### Step 4: Create Rental
```
1. Click: POST /api/rentals
2. Try it out
3. Enter:
   {
     "instru_ownership_id": 1,
     "start_date": "2026-01-20",
     "end_date": "2026-01-25"
   }
4. Execute
5. See rental created!
```

### Step 5: Pay for Rental
```
1. Click: POST /api/payments/{rental_id}/initiate
2. Try it out
3. Enter rental_id: 1
4. Execute
5. See payment initialized with Stripe client_secret
```

---

## 🔍 Understanding Responses

### Successful Request (Status 200, 201)
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "User Name",
  "created_at": "2026-01-16T12:00:00"
}
```

### Error Request (Status 400)
```json
{
  "code": "400",
  "status": "Bad Request",
  "description": "Invalid email format"
}
```

### Unauthorized (Status 401)
```json
{
  "code": "401",
  "status": "Unauthorized",
  "description": "Missing Authorization Header"
}
```

### Not Found (Status 404)
```json
{
  "code": "404",
  "status": "Not Found",
  "description": "User not found"
}
```

---

## 📋 Common Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | OK - Request succeeded | GET request returned data |
| 201 | Created - Resource created | POST request created new item |
| 400 | Bad Request - Invalid input | Missing required field |
| 401 | Unauthorized - No/invalid token | Missing authorization header |
| 403 | Forbidden - No permission | Can't access other user's data |
| 404 | Not Found - Resource missing | Invalid ID |
| 500 | Server Error - Internal error | Database connection failed |

---

## 💡 Pro Tips

### 1. Use "Try it out" for Testing
- Fastest way to test endpoints
- No need to write curl commands
- Immediate feedback

### 2. Copy Curl Commands
- After executing, scroll down
- Find "Curl" section
- Copy for use in scripts

### 3. Keep Token in Browser
- Authorize once per session
- Token stays valid for 1 hour
- No need to re-authorize for each request

### 4. Try Error Cases
- Send invalid data on purpose
- See error messages
- Understand what API expects

### 5. Read Descriptions
- Each endpoint has a description
- Shows what it does
- Shows what auth is required

---

## 🐛 Troubleshooting

### "Cannot connect to localhost:5000"
**Solution**: 
1. Make sure server is running: `python run.py`
2. Wait 5 seconds for startup
3. Check terminal for errors

### "Missing Authorization Header" Error
**Solution**:
1. You need to authenticate first
2. Click Authorize button (🔒)
3. Paste your JWT token
4. Try again

### "Token has expired"
**Solution**:
1. Get a new token by logging in
2. POST /api/auth/login
3. Copy new access_token
4. Update Authorize with new token

### Swagger UI Not Loading
**Solution**:
1. Hard refresh browser: Ctrl+Shift+R
2. Try different browser
3. Check: http://localhost:5000/swagger-ui (exact URL)

### "Cannot read properties of undefined"
**Solution**:
1. Wait a few seconds for API to fully start
2. Restart server: `python run.py`
3. Clear browser cache

---

## 🔐 Security Notes

### Your JWT Token
- ✅ Valid for 1 hour
- ✅ Don't share it publicly
- ✅ Only use on localhost for testing
- ✅ Use HTTPS in production

### Password
- ✅ Use strong password
- ✅ Not transmitted in token
- ✅ Hashed in database

### API Keys
- ✅ Keep Stripe key secret
- ✅ Store in .env file
- ✅ Never commit to git

---

## 📖 Full Documentation

See [SWAGGER_CONFIGURATION.md](SWAGGER_CONFIGURATION.md) for:
- Complete endpoint reference
- Authentication details
- Advanced configuration
- Customization guide
- Troubleshooting

---

## ✨ What's Included

✅ **Swagger UI** - Interactive documentation  
✅ **ReDoc** - Clean reading interface  
✅ **OpenAPI JSON** - Machine-readable spec  
✅ **Authentication** - JWT Bearer token support  
✅ **Try it out** - Test endpoints directly  
✅ **Curl commands** - Copy for scripting  
✅ **Error documentation** - Understand failures  

---

## 🎯 Next Steps

1. **Start server**: `python run.py`
2. **Open Swagger**: http://localhost:5000/swagger-ui
3. **Register**: POST /api/auth/register
4. **Authorize**: Click 🔒 button, paste token
5. **Try an endpoint**: Click "Try it out"
6. **Explore**: Test different endpoints

---

**Status**: ✅ READY  
**Access**: http://localhost:5000/swagger-ui  
**Configured**: January 16, 2026  

Happy API testing! 🚀
