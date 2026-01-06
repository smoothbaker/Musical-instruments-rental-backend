from flask import Flask
from flask_jwt_extended import JWTManager
from app.db import db
from app.config import Config
from flask_migrate import Migrate
from flask_smorest import Api

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    jwt = JWTManager(app)
    
    # Initialize API
    api = Api(app)
    
    # Register blueprints
    from app.routes import auth, instruments, rentals, recommendations, users, instru_ownership, dashboard
    app.register_blueprint(auth.bp)
    app.register_blueprint(instruments.bp)
    app.register_blueprint(rentals.bp)
    app.register_blueprint(recommendations.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(instru_ownership.bp)
    app.register_blueprint(dashboard.bp)
    
    return app