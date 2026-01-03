from flask import Flask
from flask_jwt_extended import JWTManager
from app.models import db
from app.config import Config
from flask_migrate import Migrate

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    jwt = JWTManager(app)
    
    # Register blueprints
    from app.routes import auth, instruments, rentals, recommendations
    app.register_blueprint(auth.bp)
    app.register_blueprint(instruments.bp)
    app.register_blueprint(rentals.bp)
    app.register_blueprint(recommendations.bp)
    
    return app