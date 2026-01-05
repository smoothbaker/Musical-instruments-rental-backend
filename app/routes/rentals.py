from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, Rental, Instrument
from datetime import datetime

bp = Blueprint('rentals', __name__, url_prefix='/api/rentals')

@bp.route('', methods=['POST'])
@jwt_required()
def create_rental():
    data = request.get_json()
    user_id = get_jwt_identity()
    
    instrument = Instrument.query.get_or_404(data['instrument_id'])
    
    if not instrument.is_available:
        return jsonify({'error': 'Instrument not available'}), 400
    
    # Parse dates
    start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
    end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
    
    # Calculate cost
    days = (end_date - start_date).days + 1
    total_cost = days * instrument.daily_rate
    
    rental = Rental(
        user_id=user_id,
        instrument_id=instrument.id,
        start_date=start_date,
        end_date=end_date,
        total_cost=total_cost,
        status='pending'
    )
    
    # Mark instrument as unavailable
    instrument.is_available = False
    
    db.session.add(rental)
    db.session.commit()
    
    return jsonify({
        'message': 'Rental created',
        'rental_id': rental.id,
        'total_cost': total_cost
    }), 201

@bp.route('', methods=['GET'])
@jwt_required()
def get_user_rentals():
    user_id = get_jwt_identity()
    rentals = Rental.query.filter_by(user_id=user_id).all()
    
    return jsonify([{
        'id': r.id,
        'instrument_id': r.instrument_id,
        'instrument_name': r.instrument.name,
        'start_date': r.start_date.isoformat(),
        'end_date': r.end_date.isoformat(),
        'total_cost': r.total_cost,
        'status': r.status
    } for r in rentals]), 200

@bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_rental(id):
    user_id = int(get_jwt_identity())  # Convert JWT identity to int for comparison
    rental = Rental.query.get_or_404(id)
    
    if rental.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({
        'id': rental.id,
        'instrument': {
            'id': rental.instrument.id,
            'name': rental.instrument.name,
            'category': rental.instrument.category
        },
        'start_date': rental.start_date.isoformat(),
        'end_date': rental.end_date.isoformat(),
        'actual_return_date': rental.actual_return_date.isoformat() if rental.actual_return_date else None,
        'total_cost': rental.total_cost,
        'status': rental.status
    }), 200

@bp.route('/<int:id>/return', methods=['POST'])
@jwt_required()
def return_rental(id):
    user_id = int(get_jwt_identity())  # Convert JWT identity to int for comparison
    rental = Rental.query.get_or_404(id)
    
    if rental.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    rental.actual_return_date = datetime.utcnow().date()
    rental.status = 'completed'
    rental.instrument.is_available = True
    
    db.session.commit()
    
    return jsonify({'message': 'Rental returned successfully'}), 200