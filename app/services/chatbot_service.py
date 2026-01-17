"""Chatbot service for instrument recommendations and music advice"""

from app.models import User, SurveyResponse, Instrument, Instru_ownership, Review
from app.db import db
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import json

# Lazy-load LLM to avoid errors if Ollama is not running
_model = None
_chain = None

def get_llm_model():
    """Lazy-load LLM model"""
    global _model
    if _model is None:
        try:
            from langchain_ollama import OllamaLLM
            _model = OllamaLLM(model="llama2", timeout=120)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Ollama LLM: {e}. Is Ollama running on localhost:11434?")
    return _model

def get_chain():
    """Lazy-load prompt chain"""
    global _chain
    if _chain is None:
        try:
            from langchain_core.prompts import ChatPromptTemplate
            from app.services.chatbot_service import template
            prompt_template = ChatPromptTemplate.from_template(template)
            model = get_llm_model()
            _chain = prompt_template | model
        except Exception as e:
            raise RuntimeError(f"Failed to initialize chatbot chain: {e}")
    return _chain


# Create the prompt template for the chatbot
template = """You are a knowledgeable and friendly chatbot assistant for a musical instruments rental platform. 
Your role is to:
1. Answer questions about musical instruments, music, and music learning
2. Recommend instruments based on user preferences, experience level, and budget
3. Provide helpful advice about instrument care and playing tips
4. Help users navigate the rental platform

Be conversational, friendly, and encouraging. Always provide accurate information about instruments.
Do not make up information about instruments or music that isn't accurate.
If you don't know something, be honest and suggest how the user might find the information.

IMPORTANT: If you're recommending instruments, provide specific, actionable suggestions based on the user's profile.

Conversation History: {context}

User Profile Information:
- Experience Level: {experience_level}
- Preferred Instruments: {preferred_instruments}
- Favorite Genres: {favorite_genres}
- Budget Range: {budget_range}
- Rental Frequency: {rental_frequency}
- Use Case: {use_case}

Available Instruments in Our System:
{available_instruments}

User Question: {question}

Provide a helpful, friendly response. If recommending instruments, suggest specific ones from our available inventory.
If you recommend instruments, end your response with a JSON block in this format:
[RECOMMENDATIONS]
{{"recommendations": [
    {{"name": "Instrument Name", "reason": "Why this is good for you"}},
    ...
]}}
[/RECOMMENDATIONS]

Assistant Response:
"""


def get_user_profile(user_id: int) -> Dict:
    """
    Fetch user's profile including survey responses and preferences.
    
    Args:
        user_id: The ID of the user
        
    Returns:
        Dictionary containing user preferences and profile data
    """
    try:
        user = User.query.get(user_id)
        if not user:
            return {}
        
        survey = SurveyResponse.query.filter_by(user_id=user_id).first()
        
        profile = {
            'user_id': user_id,
            'name': user.name,
            'experience_level': survey.experience_level if survey else 'beginner',
            'preferred_instruments': survey.preferred_instruments if survey else 'Not specified',
            'favorite_genres': survey.favorite_genres if survey else 'Not specified',
            'budget_range': survey.budget_range if survey else 'Not specified',
            'rental_frequency': survey.rental_frequency if survey else 'Not specified',
            'use_case': survey.use_case if survey else 'Not specified'
        }
        
        return profile
    except Exception as e:
        print(f"Error fetching user profile: {str(e)}")
        return {}


def get_available_instruments() -> str:
    """
    Fetch available instruments from the database.
    
    Returns:
        Formatted string of available instruments with details
    """
    try:
        instruments = db.session.query(Instru_ownership).filter_by(is_available=True).all()
        
        instruments_list = []
        for ownership in instruments:
            instruments_list.append({
                'name': ownership.instrument.name,
                'category': ownership.instrument.category,
                'condition': ownership.condition,
                'daily_rate': ownership.daily_rate,
                'location': ownership.location
            })
        
        if not instruments_list:
            return "No instruments currently available for rent."
        
        # Format as readable string
        formatted = "Available Instruments:\n"
        for inst in instruments_list[:15]:  # Limit to 15 to avoid token overload
            formatted += f"- {inst['name']} ({inst['category']}): ${inst['daily_rate']}/day, {inst['condition']} condition\n"
        
        if len(instruments_list) > 15:
            formatted += f"... and {len(instruments_list) - 15} more instruments"
        
        return formatted
    except Exception as e:
        print(f"Error fetching instruments: {str(e)}")
        return "Available instruments data unavailable"


def get_conversation_history(session_id: str, user_id: int, limit: int = 5) -> str:
    """
    Fetch conversation history for context.
    
    Args:
        session_id: The session ID for this conversation
        user_id: The user ID
        limit: Number of recent messages to include
        
    Returns:
        Formatted conversation history string
    """
    try:
        from app.models import ChatMessage
        
        messages = ChatMessage.query.filter_by(
            session_id=session_id,
            user_id=user_id
        ).order_by(ChatMessage.created_at.desc()).limit(limit * 2).all()
        
        messages.reverse()  # Show oldest first
        
        history = []
        for msg in messages:
            role = "User" if msg.message_type == "user" else "Assistant"
            history.append(f"{role}: {msg.content}")
        
        return "\n".join(history) if history else "No previous conversation history"
    except Exception as e:
        print(f"Error fetching conversation history: {str(e)}")
        return "No previous conversation history"


def extract_recommendations(response: str) -> List[Dict]:
    """
    Extract instrument recommendations from the model response.
    
    Args:
        response: The model's text response
        
    Returns:
        List of recommended instruments with reasons
    """
    try:
        if "[RECOMMENDATIONS]" in response and "[/RECOMMENDATIONS]" in response:
            start = response.find("[RECOMMENDATIONS]") + len("[RECOMMENDATIONS]")
            end = response.find("[/RECOMMENDATIONS]")
            json_str = response[start:end].strip()
            
            recommendations = json.loads(json_str)
            return recommendations.get('recommendations', [])
    except Exception as e:
        print(f"Error extracting recommendations: {str(e)}")
    
    return []


def chat_with_user(user_id: int, session_id: str, user_message: str) -> Dict:
    """
    Process user message and generate chatbot response.
    
    Args:
        user_id: The ID of the user
        session_id: The conversation session ID
        user_message: The user's message/question
        
    Returns:
        Dictionary with assistant response and context data
    """
    try:
        from app.models import ChatMessage
        
        # Get user profile and context
        user_profile = get_user_profile(user_id)
        available_instruments = get_available_instruments()
        conversation_history = get_conversation_history(session_id, user_id)
        
        # Get the chain (lazy-loaded)
        chain = get_chain()
        
        # Get response from the model
        response = chain.invoke({"context": conversation_history, 
                                "experience_level": user_profile.get('experience_level', 'beginner'),
                                "preferred_instruments": user_profile.get('preferred_instruments', 'Not specified'),
                                "favorite_genres": user_profile.get('favorite_genres', 'Not specified'),
                                "budget_range": user_profile.get('budget_range', 'Not specified'),
                                "rental_frequency": user_profile.get('rental_frequency', 'Not specified'),
                                "use_case": user_profile.get('use_case', 'Not specified'),
                                "available_instruments": available_instruments,
                                "question": user_message})
        
        # Extract recommendations from response
        recommendations = extract_recommendations(response)
        
        # Clean response by removing recommendation blocks
        clean_response = response.split("[RECOMMENDATIONS]")[0].strip()
        
        # Save messages to database
        user_msg = ChatMessage(
            user_id=user_id,
            session_id=session_id,
            message_type='user',
            content=user_message,
            context_data={'profile': user_profile}
        )
        db.session.add(user_msg)
        
        assistant_msg = ChatMessage(
            user_id=user_id,
            session_id=session_id,
            message_type='assistant',
            content=clean_response,
            context_data={
                'recommendations': recommendations,
                'profile_used': user_profile
            }
        )
        db.session.add(assistant_msg)
        db.session.commit()
        
        return {
            'session_id': session_id,
            'user_message': user_message,
            'assistant_response': clean_response,
            'recommendations': recommendations,
            'context': {
                'user_profile': user_profile,
                'experience_level': user_profile.get('experience_level'),
                'preferred_instruments': user_profile.get('preferred_instruments')
            },
            'created_at': datetime.utcnow()
        }
    
    except Exception as e:
        print(f"Error in chat_with_user: {str(e)}")
        return {
            'error': str(e),
            'assistant_response': f"I apologize, but I encountered an error processing your request. Please try again."
        }


def get_session_history(user_id: int, session_id: str) -> List[Dict]:
    """
    Get all messages in a conversation session.
    
    Args:
        user_id: The user ID
        session_id: The session ID
        
    Returns:
        List of chat messages in the session
    """
    try:
        from app.models import ChatMessage
        
        messages = ChatMessage.query.filter_by(
            user_id=user_id,
            session_id=session_id
        ).order_by(ChatMessage.created_at.asc()).all()
        
        return [msg.to_dict() for msg in messages]
    except Exception as e:
        print(f"Error fetching session history: {str(e)}")
        return []
