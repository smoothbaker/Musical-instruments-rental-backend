"""Chat message model for storing chatbot conversations"""
from app.db import db
from datetime import datetime


class ChatMessage(db.Model):
    """Store user and chatbot messages for conversation history"""
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_id = db.Column(db.String(100), nullable=False)  # Group messages by conversation session
    message_type = db.Column(db.String(20), nullable=False)  # 'user' or 'assistant'
    content = db.Column(db.Text, nullable=False)  # The actual message
    context_data = db.Column(db.JSON)  # Store metadata like user preferences used, instruments recommended
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='chat_messages', lazy=True)
    
    def to_dict(self):
        """Convert message to dictionary"""
        return {
            'id': self.id,
            'message_type': self.message_type,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
