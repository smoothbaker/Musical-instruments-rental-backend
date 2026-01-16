from marshmallow import Schema, fields

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    email = fields.Email(required=True)
    password = fields.Str(load_only=True, required=True)
    name = fields.Str(required=True)
    phone = fields.Str()
    user_type = fields.Str(required=True, validate=lambda x: x in ['owner', 'renter'])
    created_at = fields.DateTime(dump_only=True)

class UserUpdateSchema(Schema):
    email = fields.Email()
    name = fields.Str()
    phone = fields.Str()
    user_type = fields.Str(validate=lambda x: x in ['owner', 'renter'])

class InstrumentSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    category = fields.Str(required=True)
    brand = fields.Str()
    model = fields.Str()
    description = fields.Str()
    image_url = fields.Str()
    created_at = fields.DateTime(dump_only=True)

class InstruOwnershipSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    instrument_id = fields.Int(required=True)
    condition = fields.Str(validate=lambda x: x in ['new', 'good', 'fair', 'poor'])
    daily_rate = fields.Float(required=True, validate=lambda x: x > 0)
    image_url = fields.Str()
    location = fields.Str()
    is_available = fields.Bool(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    
    # Nested instrument info
    instrument = fields.Nested(InstrumentSchema, dump_only=True)

class InstruOwnershipUpdateSchema(Schema):
    condition = fields.Str(validate=lambda x: x in ['new', 'good', 'fair', 'poor'])
    daily_rate = fields.Float(validate=lambda x: x > 0)
    image_url = fields.Str()
    location = fields.Str()
    is_available = fields.Bool()

class RentalSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    instru_ownership_id = fields.Int(required=True)
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    actual_return_date = fields.Date()
    total_cost = fields.Float(dump_only=True)
    status = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    
    # Nested instru_ownership info
    instru_ownership = fields.Nested(InstruOwnershipSchema, dump_only=True)

class SurveyResponseSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    preferred_instruments = fields.Str()
    experience_level = fields.Str(validate=lambda x: x in ['beginner', 'intermediate', 'advanced'])
    favorite_genres = fields.Str()
    budget_range = fields.Str(validate=lambda x: x in ['0-25', '25-50', '50-100', '100+'])
    rental_frequency = fields.Str(validate=lambda x: x in ['rarely', 'monthly', 'weekly', 'frequently'])
    use_case = fields.Str()
    location = fields.Str()
    additional_notes = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class SurveyResponseUpdateSchema(Schema):
    preferred_instruments = fields.Str()
    experience_level = fields.Str(validate=lambda x: x in ['beginner', 'intermediate', 'advanced'])
    favorite_genres = fields.Str()
    budget_range = fields.Str(validate=lambda x: x in ['0-25', '25-50', '50-100', '100+'])
    rental_frequency = fields.Str(validate=lambda x: x in ['rarely', 'monthly', 'weekly', 'frequently'])
    use_case = fields.Str()
    location = fields.Str()
    additional_notes = fields.Str()

class PaymentSchema(Schema):
    id = fields.Int(dump_only=True)
    rental_id = fields.Int(required=True)
    renter_id = fields.Int(dump_only=True)
    owner_id = fields.Int(dump_only=True)
    amount = fields.Float(dump_only=True)
    status = fields.Str(dump_only=True)
    payment_method = fields.Str(dump_only=True)
    transaction_fee = fields.Float(dump_only=True)
    owner_payout_amount = fields.Float(dump_only=True)
    error_message = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    completed_at = fields.DateTime(dump_only=True)

class PaymentInitiateSchema(Schema):
    rental_id = fields.Int(required=True)
    # Client secret from Stripe - used to complete payment on frontend
    client_secret = fields.Str(dump_only=True)
    amount = fields.Float(dump_only=True)
    currency = fields.Str(dump_only=True)
    stripe_public_key = fields.Str(dump_only=True)

class PaymentConfirmSchema(Schema):
    rental_id = fields.Int(required=True)
    stripe_payment_intent_id = fields.Str(required=True)

class PaymentListSchema(Schema):
    id = fields.Int(dump_only=True)
    rental_id = fields.Int(dump_only=True)
    amount = fields.Float(dump_only=True)
    status = fields.Str(dump_only=True)
    owner_payout_amount = fields.Float(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    completed_at = fields.DateTime(dump_only=True)