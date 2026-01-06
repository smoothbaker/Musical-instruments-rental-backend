from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.db import db
from app.models import Instru_ownership, Instrument, User
from app.schemas import InstruOwnershipSchema, InstruOwnershipUpdateSchema

bp = Blueprint('instru_ownership', __name__, url_prefix='/api/instru-ownership')

@bp.route('')
class InstruOwnershipList(MethodView):
    @bp.response(200, InstruOwnershipSchema(many=True))
    def get(self):
        """Get all available instruments for rent (public)"""
        ownerships = Instru_ownership.query.filter_by(is_available=True).all()
        return ownerships

    @bp.arguments(InstruOwnershipSchema)
    @bp.response(201, InstruOwnershipSchema)
    @jwt_required()
    def post(self, ownership_data):
        """Create a new instrument ownership (owners only)"""
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if user.user_type != 'owner':
            abort(403, message="Only owners can add instruments for rent")
        
        # Check if instrument exists, if not create it
        instrument = Instrument.query.get(ownership_data['instrument_id'])
        if not instrument:
            abort(400, message="Instrument not found. Please create the instrument first.")
        
        ownership = Instru_ownership(
            user_id=user_id,
            instrument_id=ownership_data['instrument_id'],
            condition=ownership_data.get('condition', 'good'),
            daily_rate=ownership_data['daily_rate'],
            image_url=ownership_data.get('image_url'),
            location=ownership_data.get('location')
        )
        
        db.session.add(ownership)
        db.session.commit()
        return ownership

@bp.route('/my-instruments')
class MyInstruments(MethodView):
    @bp.response(200, InstruOwnershipSchema(many=True))
    @jwt_required()
    def get(self):
        """Get current user's owned instruments (owners only)"""
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if user.user_type != 'owner':
            abort(403, message="Only owners can view their instruments")
        
        ownerships = Instru_ownership.query.filter_by(user_id=user_id).all()
        return ownerships

@bp.route('/<int:ownership_id>')
class InstruOwnershipResource(MethodView):
    @bp.response(200, InstruOwnershipSchema)
    def get(self, ownership_id):
        """Get specific instrument ownership details"""
        ownership = Instru_ownership.query.get_or_404(ownership_id)
        return ownership

    @bp.arguments(InstruOwnershipUpdateSchema)
    @bp.response(200, InstruOwnershipSchema)
    @jwt_required()
    def put(self, update_data, ownership_id):
        """Update instrument ownership (owner only)"""
        user_id = int(get_jwt_identity())
        ownership = Instru_ownership.query.get_or_404(ownership_id)
        
        if ownership.user_id != user_id:
            abort(403, message="You can only update your own instruments")
        
        for key, value in update_data.items():
            setattr(ownership, key, value)
        
        db.session.commit()
        return ownership

    @bp.response(204)
    @jwt_required()
    def delete(self, ownership_id):
        """Delete instrument ownership (owner only)"""
        user_id = int(get_jwt_identity())
        ownership = Instru_ownership.query.get_or_404(ownership_id)
        
        if ownership.user_id != user_id:
            abort(403, message="You can only delete your own instruments")
        
        # Check if there are active rentals
        if ownership.rentals and any(r.status in ['pending', 'active'] for r in ownership.rentals):
            abort(400, message="Cannot delete instrument with active rentals")
        
        db.session.delete(ownership)
        db.session.commit()