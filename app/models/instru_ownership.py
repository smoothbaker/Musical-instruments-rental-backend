from app.db import db
from datetime import datetime

class Instru_ownership(db.Model):
    __tablename__ = 'instruments ownership'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    instrument_id = db.Column(db.Integer, db.ForeignKey('instruments.id'), nullable=False)
    condition = db.Column(db.String(20))  # new, good, fair
    daily_rate = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(255))
    location = db.Column(db.String(100))
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='instru_ownerships')
    instrument = db.relationship('Instrument', back_populates='instru_ownerships')
    rentals = db.relationship('Rental', back_populates='instru_ownership')
    