from app.db import db
from datetime import datetime

class Instrument(db.Model):
    __tablename__ = 'instruments'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # guitar, piano, drums, etc.
    brand = db.Column(db.String(50))
    model = db.Column(db.String(50))
    condition = db.Column(db.String(20))  # new, good, fair
    daily_rate = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    location = db.Column(db.String(100))
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    rentals = db.relationship('Rental', backref='instrument', lazy=True)
    reviews = db.relationship('Review', backref='instrument', lazy=True)