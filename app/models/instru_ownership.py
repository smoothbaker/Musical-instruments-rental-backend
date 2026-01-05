from app.db import db
from datetime import datetime

class Instru_ownership(db.Model):
    __tablename__ = 'instruments ownership'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    instrument_id = db.Column(db.Integer, db.ForeignKey('instruments.id'), nullable=False)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('instru_ownerships', lazy=True))
    instrument = db.relationship('Instrument', backref=db.backref('instru_ownerships', lazy=True))
    