from app.db import db
from datetime import datetime
class Rental(db.Model):
    __tablename__ = 'rentals'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    instrument_id = db.Column(db.Integer, db.ForeignKey('instruments.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    actual_return_date = db.Column(db.Date)
    total_cost = db.Column(db.Float)
    status = db.Column(db.String(20), default='pending')  # pending, active, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)