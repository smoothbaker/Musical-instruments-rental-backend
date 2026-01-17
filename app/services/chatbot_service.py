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
        
        # Try to use Ollama LLM first
        try:
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
            
        except (RuntimeError, Exception) as e:
            # Fallback to rule-based chatbot if Ollama is not available
            print(f"Ollama unavailable, using fallback chatbot: {str(e)}")
            clean_response, recommendations = fallback_chatbot_response(
                user_message, user_profile, available_instruments
            )
        
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


def fallback_chatbot_response(user_message: str, user_profile: Dict, available_instruments: str) -> Tuple[str, List[Dict]]:
    """
    Fallback rule-based chatbot when Ollama is unavailable.
    
    Args:
        user_message: User's question
        user_profile: User profile data
        available_instruments: Available instruments string
        
    Returns:
        Tuple of (response_text, recommendations_list)
    """
    message_lower = user_message.lower()
    recommendations = []
    
    # Extract experience level and budget
    experience = user_profile.get('experience_level', 'beginner')
    budget_range = user_profile.get('budget_range', 'Not specified')
    preferred = user_profile.get('preferred_instruments', '').lower()
    
    # Recommendation keywords
    recommendation_keywords = ['recommend', 'suggest', 'what should', 'which instrument', 
                               'best for me', 'looking for', 'want to', 'interested in']
    
    # Check if user is asking for recommendations
    is_recommendation_request = any(keyword in message_lower for keyword in recommendation_keywords)
    
    if is_recommendation_request:
        # Build personalized recommendations based on profile
        response = f"Based on your profile (experience level: {experience}), I'd be happy to recommend some instruments!\n\n"
        
        # Parse available instruments
        try:
            instruments_data = []
            if "Available Instruments:" in available_instruments:
                lines = available_instruments.split('\n')[1:]  # Skip header
                for line in lines:
                    if line.strip() and line.startswith('-'):
                        # Parse instrument info
                        instruments_data.append(line.strip('- '))
            
            # Filter and recommend based on experience and budget
            if experience == 'beginner':
                response += "As a beginner, I recommend starting with instruments that are:\n"
                response += "- Easy to learn and forgiving\n"
                response += "- Affordable to rent\n"
                response += "- Widely available\n\n"
                
                # Recommend guitars for beginners
                guitar_instruments = [inst for inst in instruments_data if 'guitar' in inst.lower()]
                if guitar_instruments:
                    response += "Perfect starter options:\n"
                    for inst in guitar_instruments[:3]:
                        name = inst.split('(')[0].strip()
                        response += f"- {name}\n"
                        recommendations.append({
                            'name': name,
                            'reason': 'Great for beginners, easy to learn'
                        })

            
            elif experience == 'intermediate' or experience == 'advanced':
                response += f"As an {experience} player, you might enjoy:\n"
                # Recommend based on preferred instruments if specified
                if preferred and preferred != 'not specified':
                    matching_instruments = [inst for inst in instruments_data 
                                           if any(pref in inst.lower() for pref in preferred.split(','))]
                    if matching_instruments:
                        for inst in matching_instruments[:5]:
                            name = inst.split('(')[0].strip()
                            response += f"- {name}\n"
                            recommendations.append({
                                'name': name,
                                'reason': f'Matches your preference for {preferred}'
                            })
                else:
                    # Show variety
                    for inst in instruments_data[:5]:
                        name = inst.split('(')[0].strip()
                        response += f"- {name}\n"
                        recommendations.append({
                            'name': name,
                            'reason': f'Suitable for {experience} players'
                        })
            
            if not recommendations:
                response += "Unfortunately, we don't have instruments matching your exact preferences right now, but here's what's available:\n"
                for inst in instruments_data[:5]:
                    name = inst.split('(')[0].strip()
                    response += f"- {name}\n"
        
        except Exception as e:
            response += "Check out our available instruments in the catalog!"
        
        response += "\n\nWould you like more details about any specific instrument?"
    
    # General questions about instruments
    elif 'guitar' in message_lower:
        response = "Guitars are wonderful instruments! They're versatile and great for many music styles.\n\n"
        if experience == 'beginner':
            response += "For beginners, I recommend starting with an acoustic guitar. It's easier on the fingers and helps build good technique.\n\n"
        response += "We have several guitars available for rent. Would you like me to show you our guitar options based on your budget?"
        
    elif 'piano' in message_lower or 'keyboard' in message_lower:
        response = "Pianos and keyboards are excellent choices! They provide a strong foundation for understanding music theory.\n\n"
        if experience == 'beginner':
            response += "As a beginner, a keyboard might be more practical - it's portable and usually more affordable to rent.\n\n"
        response += "Let me know if you'd like recommendations based on your specific needs!"
        
    elif 'drums' in message_lower:
        response = "Drums are fantastic for rhythm and coordination! \n\n"
        if experience == 'beginner':
            response += "Beginners often start with practice pads before moving to full kits. Would you like to explore our drum options?"
        else:
            response += "Check out our available drum kits - we have options for all skill levels!"
    
    # Budget questions
    elif 'cost' in message_lower or 'price' in message_lower or 'budget' in message_lower:
        response = "Our rental prices vary based on the instrument and condition:\n\n"
        response += "You can find instruments ranging from $25/day to $100+/day.\n"
        if budget_range != 'Not specified':
            response += f"\nBased on your budget range (${budget_range}/day), I can help you find suitable options. Just let me know what type of instrument you're interested in!"
        else:
            response += "\nWhat's your budget range? I can help you find the perfect instrument within your price range."
    
    # Help/general questions  
    elif any(word in message_lower for word in ['help', 'how', 'what', 'hello', '  hi']):
        response = f"Hello! I'm your musical instruments rental assistant. 👋\n\n"
        response += "I can help you with:\n"
        response += "- Finding the perfect instrument based on your experience and budget\n"
        response += "- Answering questions about specific instruments\n"
        response += "- Providing rental information and pricing\n"
        response += "- Giving tips for beginners\n\n"
        response += f"I see you're a {experience} player. "
        response += "What instrument are you interested in learning or renting?"
    
    # Default response
    else:
        response = "That's an interesting question! I'd be happy to help you find the right instrument.\n\n"
        response += f"Based on your profile:\n"
        response += f"- Experience: {experience}\n"
        if budget_range != 'Not specified':
            response += f"- Budget: ${budget_range}/day\n"
        response += "\nCould you tell me more about what you're looking for? Are you interested in:\n"
        response += "- String instruments (guitar, violin, etc.)\n"
        response += "- Keyboards/pianos\n"
        response += "- Percussion (drums)\n"
        response += "- Wind instruments\n\n"
        response += "Or would you like me to recommend something based on your profile?"
    
    return response, recommendations



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
