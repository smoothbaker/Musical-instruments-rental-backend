from app.db import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    user_type = db.Column(db.String(20), nullable=False, default='renter')  # 'owner' or 'renter'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    rentals = db.relationship('Rental', back_populates='user', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True, overlaps="renter")
    instru_ownerships = db.relationship('Instru_ownership', back_populates='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
