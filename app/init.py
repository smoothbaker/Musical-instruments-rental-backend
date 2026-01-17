from flask import Flask, app, redirect, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS  # Add CORS support for frontend
from app.db import db
from app.config import Config
from flask_smorest import Api

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)  
    
    # Initialize extensions
    db.init_app(app)
    
    # Enable CORS for all routes (required for frontend to connect)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Optional: Initialize Flask-Migrate for migrations
    try:
        from flask_migrate import Migrate
        migrate = Migrate(app, db)
    except ImportError:
        pass  # Migrations not required for basic app
    
    jwt = JWTManager(app)
    
    # Initialize API with Swagger/OpenAPI documentation
    # This MUST be initialized BEFORE registering blueprints
    api = Api(app)
    
    # Configure security schemes for Swagger UI Authorize button
    # This enables users to authenticate and test protected endpoints
    api.spec.components.security_scheme("Bearer", {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "JWT authentication token. Obtain from /api/auth/login. Click 'Authorize' and enter: Bearer <your-token>"
    })
    
    # Import blueprint modules
    from app.routes import (
        auth, instruments, rentals, recommendations, users, 
        instru_ownership, dashboard, survey, payments, reviews, chatbot
    )
    
    # Register all blueprints with the Api object for Flask-Smorest documentation
    # Using api.register_blueprint() ensures they appear in Swagger documentation
    api.register_blueprint(auth.blp)
    api.register_blueprint(instruments.blp)
    api.register_blueprint(rentals.blp)
    api.register_blueprint(recommendations.bp)
    api.register_blueprint(users.blp)
    api.register_blueprint(instru_ownership.bp)
    api.register_blueprint(dashboard.bp)
    api.register_blueprint(survey.bp)
    api.register_blueprint(payments.bp)
    api.register_blueprint(reviews.blp)
    api.register_blueprint(chatbot.blp)
    
    # Add helpful root endpoints (outside of API documentation)
    @app.route('/')
    def root():
        """Root endpoint with API information"""
        return jsonify({
            'name': 'Musical Instruments Rental API',
            'version': '1.0',
            'status': 'running',
            'documentation': {
                'swagger': '/swagger-ui',
                'redoc': '/redoc',
                'openapi': '/swagger.json'
            },
            'endpoints': {
                'auth': '/api/auth',
                'instruments': '/api/instruments',
                'rentals': '/api/rentals',
                'payments': '/api/payments',
                'reviews': '/api/reviews',
                'chatbot': '/api/chatbot',
                'dashboard': '/api/dashboard',
                'users': '/api/users'
            }
        }), 200
    
    @app.route('/health')
    def health():
        """Health check endpoint"""
        return jsonify({'status': 'healthy', 'service': 'Musical Instruments Rental API'}), 200
    
    @app.route('/api')
    @app.route('/api/')
    def api_root():
        """API root endpoint - redirects to documentation"""
        return redirect('/swagger-ui', code=302)
    
    return app