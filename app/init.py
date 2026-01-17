from flask import Flask
from flask_jwt_extended import JWTManager
from app.db import db
from app.config import Config
from flask_smorest import Api

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    
    # Optional: Initialize Flask-Migrate for migrations
    try:
        from flask_migrate import Migrate
        migrate = Migrate(app, db)
    except ImportError:
        pass  # Migrations not required for basic app
    
    jwt = JWTManager(app)
    
    # Initialize API with Swagger/OpenAPI documentation
    api = Api(app)
    
    # Register blueprints
    from app.routes import auth, instruments, rentals, recommendations, users, instru_ownership, dashboard, survey, payments, reviews, chatbot
    app.register_blueprint(auth.bp)
    app.register_blueprint(instruments.bp)
    app.register_blueprint(rentals.bp)
    app.register_blueprint(recommendations.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(instru_ownership.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(survey.bp)
    app.register_blueprint(payments.bp)
    app.register_blueprint(reviews.blp)
    app.register_blueprint(chatbot.blp)
    
    return app