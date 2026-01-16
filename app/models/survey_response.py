from app.db import db
from datetime import datetime

class SurveyResponse(db.Model):
    __tablename__ = 'survey_responses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # Instrument preferences (comma-separated or JSON)
    preferred_instruments = db.Column(db.String(500))  # e.g., "guitar,piano,drums"
    
    # Experience level
    experience_level = db.Column(db.String(50))  # beginner, intermediate, advanced
    
    # Music genres
    favorite_genres = db.Column(db.String(500))  # e.g., "rock,jazz,classical"
    
    # Budget
    budget_range = db.Column(db.String(50))  # e.g., "0-25", "25-50", "50-100", "100+"
    
    # Rental frequency
    rental_frequency = db.Column(db.String(50))  # rarely, monthly, weekly, frequently
    
    # Primary use case
    use_case = db.Column(db.String(200))  # e.g., "hobby, professional, learning, jamming with friends"
    
    # Location preference
    location = db.Column(db.String(100))
    
    # Additional notes/preferences
    additional_notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('survey_response', uselist=False))
    
    def __repr__(self):
        return f'<SurveyResponse {self.user_id}>'
