"""Routes for chatbot functionality"""

from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.db import db
from app.models import ChatMessage, User
from app.schemas import ChatQuerySchema, ChatResponseSchema, ChatMessageSchema
from app.services.chatbot_service import chat_with_user, get_session_history
import uuid

blp = Blueprint('chatbot', __name__, url_prefix='/api/chatbot', description='Chatbot endpoints')


@blp.route('/chat')
class ChatbotChat(MethodView):
    """Main endpoint for chatbot interaction"""
    
    @blp.arguments(ChatQuerySchema)
    @blp.response(200, ChatResponseSchema)
    @jwt_required()
    def post(self, args):
        """Send a message to the chatbot and get a response"""
        user_id = int(get_jwt_identity())
        user = User.query.get_or_404(user_id)
        
        session_id = args.get('session_id')
        if not session_id:
            # Generate a new session ID if not provided
            session_id = str(uuid.uuid4())
        
        user_message = args.get('message')
        if not user_message or not user_message.strip():
            abort(400, message="Message cannot be empty")
        
        # Get chatbot response
        response = chat_with_user(user_id, session_id, user_message)
        
        if 'error' in response:
            abort(500, message=response['error'])
        
        return response


@blp.route('/history/<session_id>')
class ChatbotHistory(MethodView):
    """Get conversation history for a session"""
    
    @blp.response(200, ChatMessageSchema(many=True))
    @jwt_required()
    def get(self, session_id):
        """Get all messages in a conversation session"""
        user_id = int(get_jwt_identity())
        
        messages = ChatMessage.query.filter_by(
            user_id=user_id,
            session_id=session_id
        ).order_by(ChatMessage.created_at.asc()).all()
        
        if not messages:
            abort(404, message=f"No conversation history found for session {session_id}")
        
        return messages


@blp.route('/sessions')
class ChatbotSessions(MethodView):
    """Get all conversation sessions for the current user"""
    
    @blp.response(200)
    @jwt_required()
    def get(self):
        """Get all session IDs for the current user"""
        user_id = int(get_jwt_identity())
        
        # Get unique session IDs for this user
        sessions = db.session.query(ChatMessage.session_id).filter_by(
            user_id=user_id
        ).distinct().all()
        
        session_list = []
        for (session_id,) in sessions:
            # Get first and last message for each session
            first_msg = ChatMessage.query.filter_by(
                user_id=user_id,
                session_id=session_id
            ).order_by(ChatMessage.created_at.asc()).first()
            
            last_msg = ChatMessage.query.filter_by(
                user_id=user_id,
                session_id=session_id
            ).order_by(ChatMessage.created_at.desc()).first()
            
            session_list.append({
                'session_id': session_id,
                'started_at': first_msg.created_at if first_msg else None,
                'last_message_at': last_msg.created_at if last_msg else None,
                'message_count': ChatMessage.query.filter_by(
                    user_id=user_id,
                    session_id=session_id
                ).count()
            })
        
        return {
            'sessions': session_list,
            'total_sessions': len(session_list)
        }


@blp.route('/ask-instrument-question')
class AskInstrumentQuestion(MethodView):
    """Convenience endpoint for instrument-related questions"""
    
    @blp.arguments(ChatQuerySchema)
    @blp.response(200, ChatResponseSchema)
    @jwt_required()
    def post(self, args):
        """Ask the chatbot about instruments and get recommendations"""
        user_id = int(get_jwt_identity())
        
        session_id = args.get('session_id', str(uuid.uuid4()))
        question = args.get('message')
        
        if not question:
            abort(400, message="Question cannot be empty")
        
        # Enhance question context
        enhanced_question = f"Regarding musical instruments: {question}"
        
        response = chat_with_user(user_id, session_id, enhanced_question)
        
        if 'error' in response:
            abort(500, message=response['error'])
        
        return response


@blp.route('/recommend-for-me')
class RecommendForMe(MethodView):
    """Get personalized instrument recommendations based on user profile"""
    
    @blp.arguments(ChatQuerySchema)
    @blp.response(200, ChatResponseSchema)
    @jwt_required()
    def post(self, args):
        """Get personalized instrument recommendations"""
        user_id = int(get_jwt_identity())
        
        session_id = args.get('session_id', str(uuid.uuid4()))
        preference_question = args.get('message', '')
        
        # Build recommendation request
        recommendation_prompt = f"""Based on my profile, can you recommend instruments that would be perfect for me? 
        {preference_question if preference_question else 'Consider my experience level, budget, and preferred genres.'}
        Please suggest 3-5 specific instruments from your available inventory that match my profile."""
        
        response = chat_with_user(user_id, session_id, recommendation_prompt)
        
        if 'error' in response:
            abort(500, message=response['error'])
        
        return response


@blp.route('/clear-session/<session_id>')
class ClearSession(MethodView):
    """Clear conversation history for a session"""
    
    @blp.response(200)
    @jwt_required()
    def delete(self, session_id):
        """Delete all messages in a conversation session"""
        user_id = int(get_jwt_identity())
        
        # Delete messages only if they belong to the current user
        deleted_count = ChatMessage.query.filter_by(
            user_id=user_id,
            session_id=session_id
        ).delete()
        
        db.session.commit()
        
        return {
            'message': f'Cleared {deleted_count} messages from session {session_id}',
            'deleted_count': deleted_count
        }
