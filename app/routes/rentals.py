from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.db import db
from app.models import Rental, Instru_ownership
from app.schemas import RentalSchema
from datetime import datetime, timezone

blp = Blueprint('rentals', __name__, url_prefix='/api/rentals', description='Rental management endpoints')

@blp.route('')
class RentalList(MethodView):
    @blp.arguments(RentalSchema)
    @blp.response(201, RentalSchema)
    @jwt_required()
    def post(self, rental_data):
        """Create a new rental"""
        user_id = int(get_jwt_identity())

        ownership = Instru_ownership.query.get_or_404(rental_data['instru_ownership_id'])

        if not ownership.is_available:
            abort(400, message="Instrument not available")

        if ownership.user_id == user_id:
            abort(400, message="You cannot rent your own instrument")

        # Parse dates
        start_date = rental_data['start_date']
        end_date = rental_data['end_date']

        # Calculate cost
        days = (end_date - start_date).days + 1
        total_cost = days * ownership.daily_rate

        rental = Rental(
            user_id=user_id,
            instru_ownership_id=ownership.id,
            start_date=start_date,
            end_date=end_date,
            total_cost=total_cost,
            status='pending'
        )

        # Mark ownership as unavailable
        ownership.is_available = False

        db.session.add(rental)
        db.session.commit()

        return rental

    @blp.response(200, RentalSchema(many=True))
    @jwt_required()
    def get(self):
        """Get current user's rentals"""
        user_id = int(get_jwt_identity())
        rentals = Rental.query.filter_by(user_id=user_id).all()
        return rentals

@blp.route('/<int:rental_id>')
class RentalResource(MethodView):
    @blp.response(200, RentalSchema)
    @jwt_required()
    def get(self, rental_id):
        """Get rental details"""
        user_id = int(get_jwt_identity())
        rental = Rental.query.get_or_404(rental_id)

        if rental.user_id != user_id:
            abort(403, message="Unauthorized")

        return rental

    @blp.response(204)
    @jwt_required()
    def delete(self, rental_id):
        """Cancel rental (if still pending)"""
        user_id = int(get_jwt_identity())
        rental = Rental.query.get_or_404(rental_id)

        if rental.user_id != user_id:
            abort(403, message="Unauthorized")

        if rental.status != 'pending':
            abort(400, message="Cannot cancel rental that is already active")

        # Make ownership available again
        rental.instru_ownership.is_available = True

        db.session.delete(rental)
        db.session.commit()

@blp.route('/<int:rental_id>/return')
class ReturnRental(MethodView):
    @blp.response(200)
    @jwt_required()
    def post(self, rental_id):
        """Return rental"""
        user_id = int(get_jwt_identity())
        rental = Rental.query.get_or_404(rental_id)

        if rental.user_id != user_id:
            abort(403, message="Unauthorized")

        rental.actual_return_date = datetime.now(timezone.utc).date()
        rental.status = 'completed'
        rental.instru_ownership.is_available = True

        db.session.commit()

        return {'message': 'Rental returned successfully'}