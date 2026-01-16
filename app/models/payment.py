from app.db import db
from datetime import datetime

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    rental_id = db.Column(db.Integer, db.ForeignKey('rentals.id'), nullable=False)
    renter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending, completed, failed, refunded
    payment_method = db.Column(db.String(50))  # stripe, paypal, etc
    # IMPORTANT: We store the Stripe token/ID, NOT the card details
    stripe_payment_intent_id = db.Column(db.String(255), unique=True)
    stripe_charge_id = db.Column(db.String(255), unique=True)
    # Payout tracking for owner
    stripe_transfer_id = db.Column(db.String(255))
    stripe_payout_id = db.Column(db.String(255))
    transaction_fee = db.Column(db.Float, default=0)  # Platform fee
    owner_payout_amount = db.Column(db.Float)  # Amount owner receives after fees
    
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    rental = db.relationship('Rental', backref='payment')
    renter = db.relationship('User', foreign_keys=[renter_id], backref='payments_made')
    owner = db.relationship('User', foreign_keys=[owner_id], backref='payments_received')
    
    def __repr__(self):
        return f'<Payment {self.id}: ${self.amount} for Rental {self.rental_id}>'
