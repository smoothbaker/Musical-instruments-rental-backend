from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, Instrument, Rental, Review
from sqlalchemy import func

bp = Blueprint('recommendations', __name__, url_prefix='/api/recommendations')

@bp.route('', methods=['GET'])
@jwt_required()
def get_recommendations():
    user_id = get_jwt_identity()
    
    # Get user's rental history
    user_rentals = Rental.query.filter_by(user_id=user_id).all()
    rented_categories = [r.instrument.category for r in user_rentals]
    
    recommendations = []
    
    # Strategy 1: Similar instruments to what user has rented
    if rented_categories:
        similar_instruments = Instrument.query.filter(
            Instrument.category.in_(rented_categories),
            Instrument.is_available == True
        ).limit(5).all()
        recommendations.extend(similar_instruments)
    
    # Strategy 2: Popular instruments (most rented)
    popular = db.session.query(
        Instrument,
        func.count(Rental.id).label('rental_count')
    ).join(Rental).filter(
        Instrument.is_available == True
    ).group_by(Instrument.id).order_by(
        func.count(Rental.id).desc()
    ).limit(5).all()
    
    recommendations.extend([p[0] for p in popular])
    
    # Strategy 3: Highest rated instruments
    top_rated = db.session.query(
        Instrument,
        func.avg(Review.rating).label('avg_rating')
    ).join(Review).filter(
        Instrument.is_available == True
    ).group_by(Instrument.id).order_by(
        func.avg(Review.rating).desc()
    ).limit(5).all()
    
    recommendations.extend([t[0] for t in top_rated])
    
    # Remove duplicates while preserving order
    seen = set()
    unique_recommendations = []
    for instrument in recommendations:
        if instrument.id not in seen:
            seen.add(instrument.id)
            unique_recommendations.append(instrument)
    
    return jsonify([{
        'id': i.id,
        'name': i.name,
        'category': i.category,
        'brand': i.brand,
        'daily_rate': i.daily_rate,
        'image_url': i.image_url
    } for i in unique_recommendations[:10]]), 200