# Swagger/OpenAPI Configuration Guide

## Overview

Your Musical Instruments Rental API now has **fully configured Swagger/OpenAPI documentation** with interactive API testing capabilities.

## ✅ What's Configured

### 1. Swagger UI
- **URL**: http://localhost:5000/swagger-ui
- **Features**:
  - Interactive API documentation
  - Try-it-out functionality (send test requests)
  - Real-time request/response examples
  - Authentication support (Bearer token)
  - Schema validation

### 2. ReDoc (Alternative Documentation)
- **URL**: http://localhost:5000/redoc
- **Features**:
  - Clean, readable API documentation
  - Search functionality
  - Sidebar navigation
  - Great for production documentation

### 3. OpenAPI JSON Specification
- **URL**: http://localhost:5000/swagger.json
- **Purpose**: Machine-readable API specification
- **Use Cases**:
  - Code generation
  - Client library creation
  - API monitoring tools
  - Integration with third-party tools

## 🚀 Getting Started

### Step 1: Start the API Server
```bash
python run.py
```

### Step 2: Open Swagger UI
Navigate to: **http://localhost:5000/swagger-ui**

### Step 3: Authenticate
1. Click the "Authorize" button (🔒) at the top
2. Click on "Bearer (http)" security scheme
3. Enter your JWT token (after login)
4. Click "Authorize"

### Step 4: Try an Endpoint
1. Find an endpoint (e.g., GET /api/users/profile)
2. Click "Try it out"
3. Click "Execute"
4. View the request and response

## 📖 Documentation Features

### Auto-Generated from Code
Swagger automatically generates documentation from:
- Route definitions (Flask-Smorest decorators)
- Request/response schemas (Marshmallow)
- Function docstrings
- Model definitions

### Response Examples
Each endpoint shows:
- Request parameters
- Request body schema
- Response codes (200, 400, 401, 404, etc.)
- Response body examples
- Error messages

### Security Documentation
- JWT Bearer token authentication
- Required vs optional fields
- Token expiration details
- Scopes and permissions

## 🔑 Authentication in Swagger

### Getting a Token

1. **Register as a New User**
   - POST `/api/auth/register`
   - Provide email, password, name, user_type
   - Response includes JWT token

2. **Login with Existing Credentials**
   - POST `/api/auth/login`
   - Provide email and password
   - Response includes JWT token

3. **Use Token in Swagger**
   - Copy the token from response
   - Click "Authorize" button
   - Paste token in the field
   - Click "Authorize"

### Example Flow

```
1. POST /api/auth/register
   Request:
   {
     "email": "test@example.com",
     "password": "password123",
     "name": "Test User",
     "user_type": "renter"
   }
   
   Response:
   {
     "user_id": 1,
     "email": "test@example.com",
     "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
   }

2. Copy access_token

3. Click Authorize button in Swagger UI

4. Paste token: eyJ0eXAiOiJKV1QiLCJhbGc...

5. Now all protected endpoints are available
```

## 📊 Available Endpoints in Swagger

### Authentication
- POST /api/auth/register
- POST /api/auth/login
- POST /api/auth/refresh

### Users
- GET /api/users/profile
- PUT /api/users/profile
- DELETE /api/users/{user_id}
- GET /api/users

### Instruments
- GET /api/instruments
- POST /api/instruments
- GET /api/instruments/{instrument_id}
- PUT /api/instruments/{instrument_id}
- DELETE /api/instruments/{instrument_id}

### Instrument Ownership
- POST /api/instru-ownership
- GET /api/instru-ownership
- GET /api/instru-ownership/{ownership_id}
- PUT /api/instru-ownership/{ownership_id}
- DELETE /api/instru-ownership/{ownership_id}

### Rentals
- POST /api/rentals
- GET /api/rentals
- GET /api/rentals/{rental_id}
- DELETE /api/rentals/{rental_id}

### Payments
- POST /api/payments/{rental_id}/initiate
- POST /api/payments/{rental_id}/confirm
- GET /api/payments
- GET /api/payments/{rental_id}
- POST /api/payments/{payment_id}/refund

### Survey
- POST /api/survey
- GET /api/survey
- GET /api/survey/{survey_id}
- PUT /api/survey/{survey_id}
- DELETE /api/survey/{survey_id}

### Reviews
- POST /api/reviews
- GET /api/reviews
- PUT /api/reviews/{review_id}
- DELETE /api/reviews/{review_id}

### Recommendations
- GET /api/recommendations
- GET /api/recommendations/{rental_id}

### Dashboard
- GET /api/dashboard/owner-stats
- GET /api/dashboard/renter-stats

## 🔐 Security Schemes

### Bearer Token (JWT)
All protected endpoints require:
```
Authorization: Bearer <YOUR_JWT_TOKEN>
```

**Where to get token**:
1. Register: POST /api/auth/register
2. Login: POST /api/auth/login

**Token format**:
- Type: JWT (JSON Web Token)
- Duration: 1 hour
- Refresh: Use refresh token for new access token

## 📋 Request/Response Examples

### Example: Create a Rental

**Request**:
```json
POST /api/rentals
Content-Type: application/json
Authorization: Bearer <token>

{
  "instru_ownership_id": 1,
  "start_date": "2026-01-20",
  "end_date": "2026-01-25"
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "user_id": 2,
  "instru_ownership_id": 1,
  "start_date": "2026-01-20",
  "end_date": "2026-01-25",
  "total_cost": 125.00,
  "status": "pending",
  "created_at": "2026-01-16T12:00:00"
}
```

### Example: Error Response

**Request**: (Invalid token)
```json
GET /api/users/profile
Authorization: Bearer invalid_token
```

**Response** (401 Unauthorized):
```json
{
  "code": "401",
  "status": "Unauthorized",
  "description": "Missing Authorization Header"
}
```

## 🛠️ Configuration Details

### In app/config.py
```python
# API Information
API_TITLE = "Musical Instruments Rental API"
API_VERSION = "v1.0.0"
API_DESCRIPTION = "Full description..."

# Swagger UI paths
OPENAPI_SWAGGER_UI_PATH = "/swagger-ui"
OPENAPI_REDOC_PATH = "/redoc"
OPENAPI_JSON_PATH = "/swagger.json"

# CDN URLs
OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
OPENAPI_REDOC_URL = "https://cdn.jsdelivr.net/npm/redoc@latest/bundles/redoc.standalone.js"

# OpenAPI specification version
OPENAPI_VERSION = "3.0.3"
```

### In app/init.py
```python
# Initialize API with documentation
api = Api(
    app,
    title=app.config['API_TITLE'],
    version=app.config['API_VERSION'],
    openapi_version=app.config['OPENAPI_VERSION'],
    info={'description': app.config['API_DESCRIPTION']},
    servers=app.config['SERVERS'],
    security={'Bearer': {...}}
)
```

## 🎯 Testing API Endpoints

### Using Swagger UI

1. **Find the endpoint** in the list
2. **Click "Try it out"**
3. **Fill in parameters/body**
4. **Click "Execute"**
5. **View response** and curl command

### Example Test Flow

```
1. Click Authentication > POST /api/auth/register
2. Click "Try it out"
3. Enter:
   - email: test@example.com
   - password: test123
   - name: Test User
   - user_type: renter
4. Click "Execute"
5. Copy access_token from response
6. Click "Authorize" at top
7. Paste token in Authorization field
8. Now protected endpoints are available
```

## 📱 Try-It-Out Feature

The "Try it out" button allows you to:
- ✅ Make real API requests from the UI
- ✅ See request headers and body
- ✅ View response status and body
- ✅ Copy curl command for use elsewhere
- ✅ Test different scenarios

### Example: Creating an Instrument

```
1. Navigate to: POST /api/instruments
2. Click "Try it out"
3. Enter request body:
   {
     "name": "Acoustic Guitar",
     "category": "String",
     "brand": "Fender"
   }
4. Click "Execute"
5. See response with created instrument ID
6. Copy curl command to use elsewhere
```

## 🔗 Sharing API Documentation

### Share Swagger UI URL
```
http://localhost:5000/swagger-ui
```

### Share ReDoc URL
```
http://localhost:5000/redoc
```

### Share OpenAPI JSON
```
http://localhost:5000/swagger.json
```

### For Production
1. Update domain in config:
   ```python
   SERVERS = [
       {"url": "https://api.yourdomain.com", "description": "Production"}
   ]
   ```
2. Deploy and share: `https://api.yourdomain.com/swagger-ui`

## 🐛 Troubleshooting

### Swagger UI Not Loading
1. **Check if server is running**
   ```bash
   python run.py
   ```

2. **Verify URL is correct**
   - Should be: http://localhost:5000/swagger-ui

3. **Check browser console** for errors
   - F12 → Console tab
   - Look for any error messages

4. **Clear browser cache**
   - Hard refresh: Ctrl+Shift+R (or Cmd+Shift+R on Mac)

### "Cannot read properties of undefined" Error
- **Solution**: Wait a few seconds for API to fully start
- **Or**: Restart the server with `python run.py`

### Endpoints Not Showing in Swagger
1. **Verify blueprint is registered** in app/init.py
2. **Check blueprint has `@bp.response` decorator** on endpoints
3. **Restart server** after adding new endpoints
4. **Clear browser cache** and refresh

### Authentication Not Working
1. **Get a token** first:
   - POST /api/auth/register
   - POST /api/auth/login
2. **Copy the access_token** from response
3. **Click Authorize button** (🔒 icon)
4. **Paste token** in Bearer token field
5. **Click Authorize**

### Token Expired
1. **Error**: "Token has expired"
2. **Solution**: Get a new token by logging in again
3. **Using refresh token** (if configured):
   ```
   POST /api/auth/refresh
   ```

## 📊 Swagger Features

### Schema Documentation
- ✅ Automatic schema generation from Marshmallow
- ✅ Field types and validation rules
- ✅ Required vs optional fields
- ✅ Default values

### Response Codes
- ✅ 200 OK - Success
- ✅ 201 Created - Resource created
- ✅ 400 Bad Request - Invalid input
- ✅ 401 Unauthorized - Missing token
- ✅ 403 Forbidden - Insufficient permissions
- ✅ 404 Not Found - Resource not found
- ✅ 500 Server Error - Internal error

### Operation Documentation
- ✅ Endpoint description
- ✅ Path/query/body parameters
- ✅ Response examples
- ✅ Error messages
- ✅ Required authentication

## 🚀 Best Practices

### For API Development
1. **Keep docstrings updated** in route handlers
2. **Use clear parameter names**
3. **Document error scenarios**
4. **Provide example requests/responses**
5. **Test endpoints in Swagger UI**

### For API Users
1. **Authenticate first** before trying endpoints
2. **Start with simple endpoints** (GET requests)
3. **Read error messages** carefully
4. **Use copy curl command** for scripting
5. **Check response codes** for errors

### For Documentation
1. **Add detailed descriptions** in config
2. **Use clear endpoint names**
3. **Document all parameters**
4. **Show example data**
5. **Keep info up to date**

## 📝 Customization

### Change Swagger Title
Edit `app/config.py`:
```python
API_TITLE = "My Custom API Title"
```

### Change API Version
```python
API_VERSION = "v2.0.0"
```

### Add API Description
```python
API_DESCRIPTION = """
Your detailed API description here.
Can include markdown, examples, etc.
"""
```

### Change Swagger UI Path
```python
OPENAPI_SWAGGER_UI_PATH = "/api-docs"  # New path
```

Then access at: `http://localhost:5000/api-docs`

## 🎓 Learning Resources

### Official Documentation
- Flask-Smorest: https://flask-smorest.readthedocs.io/
- OpenAPI 3.0: https://spec.openapis.org/oas/v3.0.3
- Swagger UI: https://swagger.io/tools/swagger-ui/
- Marshmallow: https://marshmallow.readthedocs.io/

### API Best Practices
- REST API Design: https://restfulapi.net/
- HTTP Status Codes: https://httpwg.org/specs/rfc7231.html
- JWT Auth: https://jwt.io/

## 🔄 Workflow Example

### Complete User Journey

```
1. START
   ↓
2. Open: http://localhost:5000/swagger-ui
   ↓
3. Register: POST /api/auth/register
   ↓
4. Copy access_token
   ↓
5. Click "Authorize"
   ↓
6. Paste token
   ↓
7. Try endpoints:
   - GET /api/users/profile
   - GET /api/instruments
   - POST /api/rentals
   - etc.
   ↓
8. View responses
   ↓
9. Copy curl commands for production code
   ↓
10. DONE
```

## ✅ Verification Checklist

- [ ] Swagger UI loads at http://localhost:5000/swagger-ui
- [ ] ReDoc loads at http://localhost:5000/redoc
- [ ] OpenAPI JSON available at http://localhost:5000/swagger.json
- [ ] Can authenticate with Bearer token
- [ ] Can execute requests from "Try it out"
- [ ] Response examples are shown
- [ ] Error codes are documented
- [ ] All endpoints are listed
- [ ] Schemas are properly defined
- [ ] Authentication is working

---

## 📞 Getting Help

If Swagger UI isn't working:

1. **Check server is running**
   ```bash
   python run.py
   ```

2. **Verify no errors in terminal**
   - Look for error messages
   - Check for port conflicts

3. **Try different browser**
   - Swagger works best in Chrome/Firefox
   - Try incognito/private mode

4. **Clear cache and restart**
   ```bash
   # Ctrl+Shift+Delete to clear browser cache
   # Then restart server
   python run.py
   ```

---

**Swagger Configuration**: ✅ COMPLETE  
**Status**: ✅ READY TO USE  
**Access**: http://localhost:5000/swagger-ui
