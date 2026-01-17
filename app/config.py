import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    # Default to a local SQLite database for easy local development.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Flask-Smorest API Configuration (Swagger/OpenAPI)
    API_TITLE = "Musical Instruments Rental API"
    API_VERSION = "v1.0.0"
    OPENAPI_VERSION = "3.0.3"
    
    # Swagger UI Configuration
    OPENAPI_URL_PREFIX = "/"
    OPENAPI_SWAGGER_UI_PATH = "/swagger-ui"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/"
    OPENAPI_REDOC_PATH = "/redoc"
    OPENAPI_REDOC_URL = "https://cdn.jsdelivr.net/npm/redoc@latest/bundles/redoc.standalone.js"
    
    # API Documentation
    API_DESCRIPTION = """
    A comprehensive REST API for managing musical instrument rentals.
    
    ## Features
    - User authentication and authorization (JWT)
    - Instrument catalog management
    - Rental request handling
    - Payment processing with Stripe
    - User reviews and ratings
    - AI-powered recommendations
    - Survey response collection for personalization
    - User dashboard with analytics
    
    ## Authentication
    All protected endpoints require a JWT token in the Authorization header:
    ```
    Authorization: Bearer YOUR_JWT_TOKEN
    ```
    
    Obtain a token by registering and logging in via the auth endpoints.
    
    ## Response Format
    All responses are in JSON format with consistent structure:
    ```json
    {
        "success": true,
        "data": {...},
        "message": "Optional message"
    }
    ```
    """
    
    # Security Schemes for Swagger
    API_SECURITY_SCHEMES = {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT authentication token (obtained from /api/auth/register or /api/auth/login)"
        }
    }
    
    # Server URLs for Swagger
    SERVERS = {
            "url": "http://localhost:5000",
            "description": "Development Server"
        },

    
    # Swagger UI Configuration
    OPENAPI_JSON_PATH = "/swagger.json"  # Path to OpenAPI spec JSON