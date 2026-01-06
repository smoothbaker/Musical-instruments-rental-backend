from app.db import db
from datetime import datetime

class Instrument(db.Model):
    __tablename__ = 'instruments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # guitar, piano, drums, etc.
    brand = db.Column(db.String(50))
    model = db.Column(db.String(50))
    
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    reviews = db.relationship('Review', backref='instrument', lazy=True)
    instru_ownerships = db.relationship('Instru_ownership', back_populates='instrument', lazy=True)