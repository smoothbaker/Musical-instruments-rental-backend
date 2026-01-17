from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.db import db
from app.models import Payment, Rental, Instru_ownership
from app.schemas import PaymentSchema, PaymentInitiateSchema, PaymentConfirmSchema, PaymentListSchema
import stripe
import os
from datetime import datetime

# Initialize Stripe with API key from environment
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY')
PLATFORM_FEE_PERCENT = 0.10  # 10% platform fee

bp = Blueprint('payments', __name__, url_prefix='/api/payments', description='Payment processing endpoints')

@bp.route('')
class PaymentList(MethodView):
    @bp.response(200, PaymentListSchema(many=True))
    @jwt_required()
    def get(self):
        """Get current user's payments (as renter or owner)"""
        user_id = int(get_jwt_identity())
        
        # Get payments where user is renter or owner
        payments = Payment.query.filter(
            (Payment.renter_id == user_id) | (Payment.owner_id == user_id)
        ).all()
        
        return payments

@bp.route('/<int:rental_id>/initiate')
class PaymentInitiate(MethodView):
    @bp.response(201, PaymentInitiateSchema)
    @jwt_required()
    def post(self, rental_id):
        """Initiate a payment for a rental - returns Stripe client secret"""
        user_id = int(get_jwt_identity())
        
        # Get rental
        rental = Rental.query.get_or_404(rental_id)
        
        # Verify user is the renter
        if rental.user_id != user_id:
            abort(403, message="Only the renter can pay for this rental")
        
        # Check if rental status is appropriate for payment
        if rental.status not in ['pending', 'active']:
            abort(400, message=f"Cannot pay for rental with status: {rental.status}")
        
        # Check if payment already exists and is completed
        existing_payment = Payment.query.filter_by(rental_id=rental_id, status='completed').first()
        if existing_payment:
            abort(400, message="Payment already completed for this rental")
        
        # Get ownership info
        ownership = rental.instru_ownership
        owner_id = ownership.user_id
        
        # Calculate amounts
        rental_amount = rental.total_cost
        platform_fee = round(rental_amount * PLATFORM_FEE_PERCENT, 2)
        total_amount = rental_amount + platform_fee
        owner_payout = round(rental_amount - platform_fee, 2)  # Owner gets rental amount minus platform fee
        
        # Create or get existing pending payment
        payment = Payment.query.filter_by(rental_id=rental_id, status='pending').first()
        
        if not payment:
            payment = Payment(
                rental_id=rental_id,
                renter_id=user_id,
                owner_id=owner_id,
                amount=rental_amount,
                transaction_fee=platform_fee,
                owner_payout_amount=owner_payout,
                status='pending',
                payment_method='stripe'
            )
            db.session.add(payment)
            db.session.commit()
        
        try:
            # Create Stripe Payment Intent
            # Amount in cents
            intent = stripe.PaymentIntent.create(
                amount=int(total_amount * 100),
                currency='usd',
                metadata={
                    'payment_id': payment.id,
                    'rental_id': rental_id,
                    'renter_id': user_id,
                    'owner_id': owner_id
                }
            )
            
            # Store the payment intent ID
            payment.stripe_payment_intent_id = intent.id
            db.session.commit()
            
            return {
                'client_secret': intent.client_secret,
                'amount': rental_amount,
                'currency': 'usd',
                'stripe_public_key': STRIPE_PUBLIC_KEY
            }
        
        except stripe.error.CardError as e:
            payment.status = 'failed'
            payment.error_message = str(e)
            db.session.commit()
            abort(400, message=f"Card error: {str(e)}")
        except stripe.error.StripeError as e:
            payment.status = 'failed'
            payment.error_message = str(e)
            db.session.commit()
            abort(400, message=f"Payment error: {str(e)}")

@bp.route('/<int:rental_id>/confirm')
class PaymentConfirm(MethodView):
    @bp.arguments(PaymentConfirmSchema)
    @bp.response(200, PaymentSchema)
    @jwt_required()
    def post(self, payment_data, rental_id):
        """Confirm payment after client-side Stripe processing"""
        user_id = int(get_jwt_identity())
        
        # Get rental
        rental = Rental.query.get_or_404(rental_id)
        
        # Verify user is the renter
        if rental.user_id != user_id:
            abort(403, message="Only the renter can confirm payment for this rental")
        
        # Get payment
        payment = Payment.query.filter_by(rental_id=rental_id, status='pending').first()
        if not payment:
            abort(404, message="No pending payment found for this rental")
        
        # Retrieve the PaymentIntent from Stripe to verify it's succeeded
        try:
            intent = stripe.PaymentIntent.retrieve(payment_data['stripe_payment_intent_id'])
            
            if intent.status == 'succeeded':
                # Update payment as completed
                payment.status = 'completed'
                payment.stripe_charge_id = intent.charges.data[0].id if intent.charges.data else intent.id
                payment.completed_at = datetime.utcnow()
                
                # Update rental status to active
                rental.status = 'active'
                
                # Mark instrument as rented (unavailable)
                ownership = rental.instru_ownership
                ownership.is_available = False
                
                db.session.commit()
                
                return payment
            
            elif intent.status == 'requires_payment_method':
                payment.status = 'failed'
                payment.error_message = 'Payment method required'
                db.session.commit()
                abort(400, message="Payment requires additional verification")
            
            else:
                payment.status = 'failed'
                payment.error_message = f'Payment intent status: {intent.status}'
                db.session.commit()
                abort(400, message=f"Payment not completed. Status: {intent.status}")
        
        except stripe.error.StripeError as e:
            payment.status = 'failed'
            payment.error_message = str(e)
            db.session.commit()
            abort(400, message=f"Error confirming payment: {str(e)}")

@bp.route('/<int:rental_id>')
class PaymentDetail(MethodView):
    @bp.response(200, PaymentSchema)
    @jwt_required()
    def get(self, rental_id):
        """Get payment details for a rental"""
        user_id = int(get_jwt_identity())
        
        payment = Payment.query.filter_by(rental_id=rental_id).first()
        if not payment:
            abort(404, message="Payment not found for this rental")
        
        # Verify user is renter or owner
        if payment.renter_id != user_id and payment.owner_id != user_id:
            abort(403, message="Unauthorized")
        
        return payment

@bp.route('/<int:payment_id>/refund')
class PaymentRefund(MethodView):
    @bp.response(200, PaymentSchema)
    @jwt_required()
    def post(self, payment_id):
        """Refund a completed payment (renters can request, owners can issue)"""
        user_id = int(get_jwt_identity())
        
        payment = Payment.query.get_or_404(payment_id)
        
        # Verify user is renter or owner
        if payment.renter_id != user_id and payment.owner_id != user_id:
            abort(403, message="Unauthorized")
        
        # Check if payment is completed
        if payment.status != 'completed':
            abort(400, message=f"Cannot refund payment with status: {payment.status}")
        
        try:
            # Refund the charge
            if payment.stripe_charge_id:
                refund = stripe.Refund.create(
                    charge=payment.stripe_charge_id,
                    metadata={'payment_id': payment.id}
                )
                
                payment.status = 'refunded'
                
                # Mark instrument as available again
                rental = payment.rental
                rental.status = 'cancelled'
                ownership = rental.instru_ownership
                ownership.is_available = True
                
                db.session.commit()
                
                return payment
            else:
                abort(400, message="No charge ID found for refund")
        
        except stripe.error.StripeError as e:
            payment.error_message = f"Refund failed: {str(e)}"
            db.session.commit()
            abort(400, message=f"Refund error: {str(e)}")
