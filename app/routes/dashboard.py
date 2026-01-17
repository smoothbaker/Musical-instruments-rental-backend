from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Rental, Instru_ownership
from app.schemas import RentalSchema, InstruOwnershipSchema

bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

@bp.route('/stats')
class DashboardStats(MethodView):
    @bp.response(200)
    @jwt_required()
    def get(self):
        """Get general dashboard statistics for the current user"""
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return {'error': 'User not found'}, 404
        
        # Return appropriate stats based on user type
        if user.user_type == 'renter':
            rentals = Rental.query.filter_by(user_id=user_id).all()
            return {
                'user_type': 'renter',
                'statistics': {
                    'total_rentals': len(rentals),
                    'active_rentals': len([r for r in rentals if r.status == 'active']),
                    'completed_rentals': len([r for r in rentals if r.status == 'completed']),
                    'total_spent': sum(r.total_cost or 0 for r in rentals if r.status == 'completed')
                }
            }
        else:  # owner
            ownerships = Instru_ownership.query.filter_by(user_id=user_id).all()
            owned_instrument_ids = [o.id for o in ownerships]
            rentals = Rental.query.filter(Rental.instru_ownership_id.in_(owned_instrument_ids)).all()
            
            return {
                'user_type': 'owner',
                'statistics': {
                    'total_instruments': len(ownerships),
                    'available_instruments': len([o for o in ownerships if o.is_available]),
                    'total_rentals': len(rentals),
                    'active_rentals': len([r for r in rentals if r.status == 'active']),
                    'completed_rentals': len([r for r in rentals if r.status == 'completed']),
                    'total_earned': sum(r.total_cost or 0 for r in rentals if r.status == 'completed')
                }
            }

@bp.route('/renter')
class RenterDashboard(MethodView):
    @bp.response(200)
    @jwt_required()
    def get(self):
        """Get renter's rental history and statistics"""
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)

        if user.user_type != 'renter':
            return {'error': 'This endpoint is for renters only'}, 403

        # Get all rentals for this user
        rentals = Rental.query.filter_by(user_id=user_id).all()

        # Calculate statistics
        total_rentals = len(rentals)
        active_rentals = len([r for r in rentals if r.status == 'active'])
        completed_rentals = len([r for r in rentals if r.status == 'completed'])
        total_spent = sum(r.total_cost for r in rentals if r.status == 'completed')

        # Get recent rentals (last 10)
        recent_rentals = sorted(rentals, key=lambda x: x.created_at, reverse=True)[:10]

        return {
            'user_info': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'user_type': user.user_type
            },
            'statistics': {
                'total_rentals': total_rentals,
                'active_rentals': active_rentals,
                'completed_rentals': completed_rentals,
                'total_spent': total_spent
            },
            'recent_rentals': [{
                'id': r.id,
                'instrument_name': r.instru_ownership.instrument.name,
                'start_date': r.start_date.isoformat(),
                'end_date': r.end_date.isoformat(),
                'total_cost': r.total_cost,
                'status': r.status,
                'created_at': r.created_at.isoformat()
            } for r in recent_rentals]
        }

@bp.route('/owner')
class OwnerDashboard(MethodView):
    @bp.response(200)
    @jwt_required()
    def get(self):
        """Get owner's instrument ownership and rental statistics"""
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)

        if user.user_type != 'owner':
            return {'error': 'This endpoint is for owners only'}, 403

        # Get all instruments owned by this user
        ownerships = Instru_ownership.query.filter_by(user_id=user_id).all()

        # Calculate statistics
        total_instruments = len(ownerships)
        available_instruments = len([o for o in ownerships if o.is_available])
        rented_instruments = total_instruments - available_instruments

        # Get all rentals for instruments owned by this user
        owned_instrument_ids = [o.id for o in ownerships]
        rentals = Rental.query.filter(Rental.instru_ownership_id.in_(owned_instrument_ids)).all()

        total_rentals = len(rentals)
        active_rentals = len([r for r in rentals if r.status == 'active'])
        completed_rentals = len([r for r in rentals if r.status == 'completed'])
        total_earned = sum(r.total_cost for r in rentals if r.status == 'completed')

        # Get recent rentals (last 10)
        recent_rentals = sorted(rentals, key=lambda x: x.created_at, reverse=True)[:10]

        return {
            'user_info': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'user_type': user.user_type
            },
            'instrument_statistics': {
                'total_instruments': total_instruments,
                'available_instruments': available_instruments,
                'rented_instruments': rented_instruments
            },
            'rental_statistics': {
                'total_rentals': total_rentals,
                'active_rentals': active_rentals,
                'completed_rentals': completed_rentals,
                'total_earned': total_earned
            },
            'owned_instruments': [{
                'id': o.id,
                'instrument_name': o.instrument.name,
                'category': o.instrument.category,
                'condition': o.condition,
                'daily_rate': o.daily_rate,
                'is_available': o.is_available,
                'location': o.location,
                'created_at': o.created_at.isoformat()
            } for o in ownerships],
            'recent_rentals': [{
                'id': r.id,
                'instrument_name': r.instru_ownership.instrument.name,
                'renter_name': r.user.name,
                'start_date': r.start_date.isoformat(),
                'end_date': r.end_date.isoformat(),
                'total_cost': r.total_cost,
                'status': r.status,
                'created_at': r.created_at.isoformat()
            } for r in recent_rentals]
        }