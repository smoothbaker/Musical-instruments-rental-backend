from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.db import db
from app.models import Review, Rental, Instru_ownership, User
from app.schemas import ReviewSchema, ReviewCreateSchema, ReviewUpdateSchema
from sqlalchemy import func

blp = Blueprint('reviews', 'reviews', url_prefix='/api/reviews', description='Operations on reviews')

class ReviewList(MethodView):
    """Get all reviews or filter by ownership"""
    
    @blp.response(200, ReviewSchema(many=True))
    def get(self):
        """Get all reviews with optional filtering
        
        Query Parameters:
        - instru_ownership_id: Filter by specific owned instrument copy
        - rating: Filter by rating (1-5)
        """
        instru_ownership_id = request.args.get('instru_ownership_id', type=int)
        rating = request.args.get('rating', type=int)
        
        query = Review.query
        
        if instru_ownership_id:
            query = query.filter_by(instru_ownership_id=instru_ownership_id)
        
        if rating:
            if not (1 <= rating <= 5):
                abort(400, message='Rating must be between 1 and 5')
            query = query.filter_by(rating=rating)
        
        reviews = query.order_by(Review.created_at.desc()).all()
        return reviews
    
    @jwt_required()
    @blp.arguments(ReviewCreateSchema)
    @blp.response(201, ReviewSchema)
    def post(self, args):
        """Create a review for a completed rental
        
        Renters can only review their own completed rentals.
        Each rental can only have one review.
        The review is attached to the specific instrument copy (Instru_ownership).
        """
        renter_id = get_jwt_identity()
        rental_id = args.get('rental_id')
        
        # Check if rental exists
        rental = Rental.query.get_or_404(rental_id, description='Rental not found')

        print(f"Renter ID: {renter_id}, Rental ID: {rental_id}, Rental User ID: {rental.user_id}, Rental Status: {rental.status}")

        # Verify the user is the renter
        if rental.user_id != int(renter_id):
            abort(403, message='Can only review your own rentals')
        
        # Check if rental is completed
        if rental.status != 'completed':
            abort(400, message='Can only review completed rentals')
        
        # Check if review already exists for this rental
        existing_review = Review.query.filter_by(rental_id=rental_id).first()
        if existing_review:
            abort(400, message='This rental has already been reviewed')
        
        # Create review linked to the specific instrument ownership
        review = Review(
            rental_id=rental_id,
            instru_ownership_id=rental.instru_ownership_id,
            renter_id=renter_id,
            rating=args.get('rating'),
            comment=args.get('comment')
        )
        
        db.session.add(review)
        db.session.commit()
        
        return review, 201


class ReviewDetail(MethodView):
    """Get, update, or delete a specific review"""
    
    @blp.response(200, ReviewSchema)
    def get(self, review_id):
        """Get a specific review"""
        review = Review.query.get_or_404(review_id, description='Review not found')
        return review
    
    @jwt_required()
    @blp.arguments(ReviewUpdateSchema)
    @blp.response(200, ReviewSchema)
    def put(self, args, review_id):
        """Update a review (renter only)"""
        renter_id = get_jwt_identity()
        review = Review.query.get_or_404(review_id, description='Review not found')
        
        # Verify the user is the reviewer
        if review.renter_id != renter_id:
            abort(403, message='Can only update your own reviews')
        
        # Update fields
        if 'rating' in args:
            review.rating = args['rating']
        if 'comment' in args:
            review.comment = args['comment']
        
        db.session.commit()
        return review
    
    @jwt_required()
    @blp.response(204)
    def delete(self, review_id):
        """Delete a review (renter only)"""
        renter_id = get_jwt_identity()
        review = Review.query.get_or_404(review_id, description='Review not found')
        
        # Verify the user is the reviewer
        if review.renter_id != renter_id:
            abort(403, message='Can only delete your own reviews')
        
        db.session.delete(review)
        db.session.commit()


class InstruOwnershipWithReviews(MethodView):
    """Get instrument ownership details with reviews and ratings"""
    
    @blp.response(200)
    def get(self, instru_ownership_id):
        """Get ownership details with all reviews and statistics
        
        Returns:
        - ownership: Instrument, owner, condition, rate
        - reviews: All reviews from renters who rented this specific copy
        - stats: Average rating, total count, distribution by rating
        """
        ownership = Instru_ownership.query.get_or_404(
            instru_ownership_id, 
            description='Instrument ownership not found'
        )
        
        # Get all reviews for this specific instrument ownership
        reviews = Review.query.filter_by(
            instru_ownership_id=instru_ownership_id
        ).order_by(Review.created_at.desc()).all()
        
        # Calculate statistics
        stats = {
            'average_rating': None,
            'total_reviews': len(reviews),
            'rating_distribution': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        }
        
        if reviews:
            avg_result = db.session.query(func.avg(Review.rating)).filter_by(
                instru_ownership_id=instru_ownership_id
            ).scalar()
            stats['average_rating'] = round(float(avg_result), 2) if avg_result else None
            
            # Calculate rating distribution
            for review in reviews:
                stats['rating_distribution'][review.rating] += 1
        
        # Get owner info
        owner = User.query.get(ownership.user_id)
        
        return {
            'ownership': {
                'id': ownership.id,
                'instrument': {
                    'id': ownership.instrument.id,
                    'name': ownership.instrument.name,
                    'category': ownership.instrument.category,
                    'brand': ownership.instrument.brand,
                    'model': ownership.instrument.model
                },
                'owner': {
                    'id': owner.id,
                    'name': owner.name
                },
                'condition': ownership.condition,
                'daily_rate': ownership.daily_rate,
                'location': ownership.location,
                'is_available': ownership.is_available,
                'created_at': ownership.created_at
            },
            'reviews': [
                {
                    'id': r.id,
                    'rental_id': r.rental_id,
                    'rating': r.rating,
                    'comment': r.comment,
                    'renter_name': r.renter.name,
                    'created_at': r.created_at,
                    'updated_at': r.updated_at
                }
                for r in reviews
            ],
            'stats': stats
        }


class OwnerOwnedInstruments(MethodView):
    """Get all instruments owned by a user with their reviews"""
    
    @blp.response(200)
    def get(self, owner_id):
        """Get all owned instruments with their reviews and stats
        
        Shows all instrument copies owned by the owner, each with its own review list.
        """
        # Verify owner exists
        owner = User.query.get_or_404(owner_id, description='Owner not found')
        
        # Get all owned instruments
        ownerships = Instru_ownership.query.filter_by(user_id=owner_id).all()
        
        result = {
            'owner': {
                'id': owner.id,
                'name': owner.name,
                'email': owner.email
            },
            'instruments': []
        }
        
        for ownership in ownerships:
            # Get reviews for this specific copy
            reviews = Review.query.filter_by(
                instru_ownership_id=ownership.id
            ).order_by(Review.created_at.desc()).all()
            
            # Calculate stats
            stats = {
                'average_rating': None,
                'total_reviews': len(reviews),
                'rating_distribution': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            }
            
            if reviews:
                avg_result = db.session.query(func.avg(Review.rating)).filter_by(
                    instru_ownership_id=ownership.id
                ).scalar()
                stats['average_rating'] = round(float(avg_result), 2) if avg_result else None
                
                for review in reviews:
                    stats['rating_distribution'][review.rating] += 1
            
            result['instruments'].append({
                'id': ownership.id,
                'instrument': {
                    'id': ownership.instrument.id,
                    'name': ownership.instrument.name,
                    'category': ownership.instrument.category,
                    'brand': ownership.instrument.brand,
                    'model': ownership.instrument.model
                },
                'condition': ownership.condition,
                'daily_rate': ownership.daily_rate,
                'location': ownership.location,
                'is_available': ownership.is_available,
                'review_count': len(reviews),
                'average_rating': stats['average_rating'],
                'reviews': [
                    {
                        'id': r.id,
                        'rating': r.rating,
                        'comment': r.comment,
                        'renter_name': r.renter.name,
                        'created_at': r.created_at
                    }
                    for r in reviews
                ]
            })
        
        return result


# Register views
blp.route('/')(ReviewList)
blp.route('/<int:review_id>')(ReviewDetail)
blp.route('/ownership/<int:instru_ownership_id>')(InstruOwnershipWithReviews)
blp.route('/owner/<int:owner_id>')(OwnerOwnedInstruments)
