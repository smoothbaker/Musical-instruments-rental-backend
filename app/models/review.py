from app.db import db
from datetime import datetime

class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    rental_id = db.Column(db.Integer, db.ForeignKey('rentals.id'), nullable=False, unique=True)
    instru_ownership_id = db.Column(db.Integer, db.ForeignKey('instruments ownership.id'), nullable=False)
    renter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    rental = db.relationship('Rental', back_populates='review')
    instru_ownership = db.relationship('Instru_ownership', back_populates='reviews')
    renter = db.relationship('User', foreign_keys=[renter_id])