import requests
import json
import os
from app.models import Instrument, Instru_ownership, Review
from app.db import db
from sqlalchemy import func

# Hugging Face free inference API endpoint for text classification/QA
HF_API_URL = "https://api-inference.huggingface.co/models/deepset/roberta-base-squad2"
# Using text summarization model for generating recommendations
HF_SUMMARIZATION_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
# Using zero-shot classification for categorizing instruments
HF_CLASSIFICATION_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"


def get_all_instruments_text():
    """Get all available instruments as formatted text for context"""
    ownerships = Instru_ownership.query.filter_by(is_available=True).all()
    
    instruments_text = []
    for ownership in ownerships:
        instrument = ownership.instrument
        avg_rating = db.session.query(func.avg(Review.rating)).filter_by(
            instru_ownership_id=ownership.id
        ).scalar() or 0
        
        instrument_desc = f"""
        - {instrument.name} ({instrument.category})
          Brand: {instrument.brand}, Model: {instrument.model}
          Daily Rate: ${ownership.daily_rate}
          Condition: {ownership.condition}
          Location: {ownership.location}
          Average Rating: {avg_rating:.1f}/5
          Description: {instrument.description or 'No description'}
        """
        instruments_text.append((ownership.id, instrument_desc.strip()))
    
    return instruments_text


def classify_user_needs_with_hf(user_needs, hf_token=None):
    """Use HuggingFace API to classify user needs into categories"""
    if not hf_token:
        hf_token = os.getenv("HUGGINGFACE_API_KEY", "")
    
    # Define candidate categories based on our database
    candidate_labels = [
        "beginner-friendly", "professional-grade", "budget-friendly",
        "acoustic", "electric", "percussion", "wind-instrument",
        "string-instrument", "keyboard"
    ]
    
    headers = {"Authorization": f"Bearer {hf_token}"} if hf_token else {}
    
    payload = {
        "inputs": user_needs,
        "parameters": {
            "candidate_labels": candidate_labels,
            "multi_class": True
        }
    }
    
    try:
        response = requests.post(HF_CLASSIFICATION_URL, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            # Return None if API fails, we'll use fallback method
            return None
    except Exception as e:
        print(f"HuggingFace classification error: {e}")
        return None


def extract_instrument_type_from_needs(user_needs):
    """Fallback method: Extract instrument type from user needs text"""
    instrument_types = {
        'guitar': ['guitar', 'acoustic', 'electric', 'fender', 'ibanez', 'les paul'],
        'piano': ['piano', 'keyboard', 'synthesizer', 'yamaha', 'grand piano'],
        'drums': ['drums', 'drum kit', 'percussion', 'cymbal', 'snare'],
        'violin': ['violin', 'viola', 'bow', 'classical', 'fiddle'],
        'flute': ['flute', 'piccolo', 'woodwind', 'wind instrument'],
        'bass': ['bass', 'bass guitar', 'upright', 'acoustic bass'],
    }
    
    user_needs_lower = user_needs.lower()
    matched_types = []
    
    for instrument_type, keywords in instrument_types.items():
        if any(keyword in user_needs_lower for keyword in keywords):
            matched_types.append(instrument_type)
    
    return matched_types


def score_instrument_match(ownership, user_needs, matched_types, budget=None):
    """
    Score how well an instrument matches user needs (0-100)
    """
    score = 0
    instrument = ownership.instrument
    
    # Category match (40 points)
    if instrument.category.lower() in matched_types:
        score += 40
    
    # Budget match (30 points)
    if budget:
        if ownership.daily_rate <= budget:
            score += 30
        elif ownership.daily_rate <= budget * 1.5:
            score += 15
    else:
        score += 20  # Default points if no budget specified
    
    # Rating match (20 points)
    avg_rating = db.session.query(func.avg(Review.rating)).filter_by(
        instru_ownership_id=ownership.id
    ).scalar() or 0
    
    if avg_rating >= 4.5:
        score += 20
    elif avg_rating >= 4.0:
        score += 15
    elif avg_rating >= 3.5:
        score += 10
    
    # Keyword match in description/name (10 points)
    combined_text = (instrument.name + " " + (instrument.description or "")).lower()
    if any(keyword in combined_text for keyword in user_needs.lower().split()):
        score += 10
    
    return score


def recommend_instruments_by_needs(user_needs, budget=None, experience_level=None, hf_token=None):
    """
    Main function to recommend instruments based on user needs
    Uses HuggingFace API for NLP processing and local scoring
    
    Args:
        user_needs: User's requirements as text (e.g., "beginner acoustic guitar")
        budget: Optional daily rental budget
        experience_level: Optional (beginner, intermediate, advanced)
        hf_token: HuggingFace API token (optional)
    
    Returns:
        List of recommended instruments with scores
    """
    # Get all available instruments
    all_instruments = get_all_instruments_text()
    
    if not all_instruments:
        return {
            "recommendations": [],
            "message": "No instruments available at the moment",
            "reasoning": "Database is empty"
        }
    
    # Try to classify with HuggingFace, fallback to keyword matching
    classification = classify_user_needs_with_hf(user_needs, hf_token)
    
    # Extract instrument types from needs
    matched_types = extract_instrument_type_from_needs(user_needs)
    
    # Score all available instruments
    ownerships = Instru_ownership.query.filter_by(is_available=True).all()
    scored_recommendations = []
    
    for ownership in ownerships:
        score = score_instrument_match(ownership, user_needs, matched_types, budget)
        
        if score > 0:  # Only include if there's some match
            instrument = ownership.instrument
            avg_rating = db.session.query(func.avg(Review.rating)).filter_by(
                instru_ownership_id=ownership.id
            ).scalar() or 0
            
            recommendation = {
                "id": ownership.id,
                "instrument_id": instrument.id,
                "name": instrument.name,
                "category": instrument.category,
                "brand": instrument.brand,
                "model": instrument.model,
                "description": instrument.description,
                "daily_rate": ownership.daily_rate,
                "location": ownership.location,
                "condition": ownership.condition,
                "average_rating": round(avg_rating, 2),
                "match_score": score,
                "reasoning": f"Matches your need for {matched_types[0] if matched_types else 'an instrument'} "
                            f"at ${ownership.daily_rate}/day with {avg_rating:.1f}/5 rating"
            }
            scored_recommendations.append(recommendation)
    
    # Sort by match score (descending)
    scored_recommendations.sort(key=lambda x: x['match_score'], reverse=True)
    
    # Return top 5 recommendations
    top_recommendations = scored_recommendations[:5]
    
    return {
        "recommendations": top_recommendations,
        "total_available": len(ownerships),
        "matched_count": len(scored_recommendations),
        "user_needs_analyzed": user_needs,
        "matched_categories": matched_types
    }
