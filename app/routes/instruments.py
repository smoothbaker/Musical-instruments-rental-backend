from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models import db, Instrument

bp = Blueprint('instruments', __name__, url_prefix='/api/instruments')

@bp.route('', methods=['GET'])
def get_instruments():
    # Query parameters for filtering
    category = request.args.get('category')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    available_only = request.args.get('available', type=bool, default=True)
    
    query = Instrument.query
    
    if category:
        query = query.filter_by(category=category)
    if min_price:
        query = query.filter(Instrument.daily_rate >= min_price)
    if max_price:
        query = query.filter(Instrument.daily_rate <= max_price)
    if available_only:
        query = query.filter_by(is_available=True)
    
    instruments = query.all()
    
    return jsonify([{
        'id': i.id,
        'name': i.name,
        'category': i.category,
        'brand': i.brand,
        'model': i.model,
        'condition': i.condition,
        'daily_rate': i.daily_rate,
        'description': i.description,
        'image_url': i.image_url,
        'location': i.location,
        'is_available': i.is_available
    } for i in instruments]), 200

@bp.route('/<int:id>', methods=['GET'])
def get_instrument(id):
    instrument = Instrument.query.get_or_404(id)
    
    return jsonify({
        'id': instrument.id,
        'name': instrument.name,
        'category': instrument.category,
        'brand': instrument.brand,
        'model': instrument.model,
        'condition': instrument.condition,
        'daily_rate': instrument.daily_rate,
        'description': instrument.description,
        'image_url': instrument.image_url,
        'location': instrument.location,
        'is_available': instrument.is_available
    }), 200

@bp.route('', methods=['POST'])
@jwt_required()  # Could add admin check here
def create_instrument():
    data = request.get_json()
    
    instrument = Instrument(
        name=data['name'],
        category=data['category'],
        brand=data.get('brand'),
        model=data.get('model'),
        condition=data.get('condition'),
        daily_rate=data['daily_rate'],
        description=data.get('description'),
        image_url=data.get('image_url'),
        location=data.get('location')
    )
    
    db.session.add(instrument)
    db.session.commit()
    
    return jsonify({'message': 'Instrument created', 'id': instrument.id}), 201