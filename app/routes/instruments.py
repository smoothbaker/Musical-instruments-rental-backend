from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required
from app.db import db
from app.models import Instrument, Instru_ownership
from app.schemas import InstrumentSchema

blp = Blueprint('instruments', __name__, url_prefix='/api/instruments', description='Instrument catalog endpoints')

@blp.route('')
class InstrumentList(MethodView):
    @blp.response(200, InstrumentSchema(many=True))
    def get(self):
        """Get all instruments in the catalog"""
        instruments = Instrument.query.all()
        return instruments

    @blp.arguments(InstrumentSchema)
    @blp.response(201, InstrumentSchema)
    @jwt_required()
    def post(self, instrument_data):
        """Create a new instrument in the catalog (any authenticated user)"""
        # Check if instrument with same name/brand/model already exists
        existing = Instrument.query.filter_by(
            name=instrument_data['name'],
            brand=instrument_data.get('brand'),
            model=instrument_data.get('model')
        ).first()
        
        if existing:
            abort(400, message="Similar instrument already exists in catalog")
        
        instrument = Instrument(**instrument_data)
        db.session.add(instrument)
        db.session.commit()
        return instrument

@blp.route('/<int:instrument_id>')
class InstrumentResource(MethodView):
    @blp.response(200, InstrumentSchema)
    def get(self, instrument_id):
        """Get instrument details from catalog"""
        instrument = Instrument.query.get_or_404(instrument_id)
        return instrument

    @blp.arguments(InstrumentSchema)
    @blp.response(200, InstrumentSchema)
    @jwt_required()
    def put(self, update_data, instrument_id):
        """Update instrument in catalog"""
        instrument = Instrument.query.get_or_404(instrument_id)
        
        # Prevent updating if there are active ownerships
        if instrument.instru_ownerships:
            abort(400, message="Cannot update instrument that has ownership records")
        
        for key, value in update_data.items():
            setattr(instrument, key, value)
        
        db.session.commit()
        return instrument

    @blp.response(204)
    @jwt_required()
    def delete(self, instrument_id):
        """Delete instrument from catalog"""
        instrument = Instrument.query.get_or_404(instrument_id)
        
        # Prevent deleting if there are ownerships
        if instrument.instru_ownerships:
            abort(400, message="Cannot delete instrument that has ownership records")
        
        db.session.delete(instrument)
        db.session.commit()

@blp.route('/available')
class AvailableInstruments(MethodView):
    @blp.response(200)
    def get(self):
        """Get all available instruments for rent (with ownership details)"""
        ownerships = Instru_ownership.query.filter_by(is_available=True).all()
        
        return [{
            'id': o.id,
            'instrument': {
                'id': o.instrument.id,
                'name': o.instrument.name,
                'category': o.instrument.category,
                'brand': o.instrument.brand,
                'model': o.instrument.model,
                'description': o.instrument.description
            },
            'condition': o.condition,
            'daily_rate': o.daily_rate,
            'image_url': o.image_url,
            'location': o.location,
            'owner_id': o.user_id
        } for o in ownerships]