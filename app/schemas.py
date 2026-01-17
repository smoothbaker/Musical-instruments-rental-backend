from marshmallow import Schema, fields

class UserSchema(Schema):
    class Meta:
        title = "User"
    
    id = fields.Int(dump_only=True)
    email = fields.Email(required=True)
    password = fields.Str(load_only=True, required=True)
    name = fields.Str(required=True)
    phone = fields.Str()
    user_type = fields.Str(required=True, validate=lambda x: x in ['owner', 'renter'])
    created_at = fields.DateTime(dump_only=True)

class UserUpdateSchema(Schema):
    class Meta:
        title = "UserUpdate"
    
    email = fields.Email()
    name = fields.Str()
    phone = fields.Str()
    user_type = fields.Str(validate=lambda x: x in ['owner', 'renter'])

class InstrumentSchema(Schema):
    class Meta:
        title = "Instrument"
    
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    category = fields.Str(required=True)
    brand = fields.Str()
    model = fields.Str()
    description = fields.Str()
    image_url = fields.Str()
    created_at = fields.DateTime(dump_only=True)

class InstrumentUpdateSchema(Schema):
    """Schema for updating instruments with all optional fields"""
    class Meta:
        title = "InstrumentUpdate"
    
    name = fields.Str()
    category = fields.Str()
    brand = fields.Str()
    model = fields.Str()
    description = fields.Str()
    image_url = fields.Str()

class InstruOwnershipSchema(Schema):
    class Meta:
        title = "InstruOwnership"
    
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
    class Meta:
        title = "InstruOwnershipUpdate"
    
    condition = fields.Str(validate=lambda x: x in ['new', 'good', 'fair', 'poor'])
    daily_rate = fields.Float(validate=lambda x: x > 0)
    image_url = fields.Str()
    location = fields.Str()
    is_available = fields.Bool()

class RentalSchema(Schema):
    class Meta:
        title = "Rental"
    
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
    class Meta:
        title = "SurveyResponse"
    
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    preferred_instruments = fields.Str(required=False, allow_none=True)
    experience_level = fields.Str(required=False, allow_none=True, validate=lambda x: x in ['beginner', 'intermediate', 'advanced'] if x else True)
    favorite_genres = fields.Str(required=False, allow_none=True)
    budget_range = fields.Str(required=False, allow_none=True, validate=lambda x: x in ['0-25', '25-50', '50-100', '100+'] if x else True)
    rental_frequency = fields.Str(required=False, allow_none=True, validate=lambda x: x in ['rarely', 'monthly', 'weekly', 'frequently'] if x else True)
    use_case = fields.Str(required=False, allow_none=True)
    location = fields.Str(required=False, allow_none=True)
    additional_notes = fields.Str(required=False, allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class SurveyResponseUpdateSchema(Schema):
    class Meta:
        title = "SurveyResponseUpdate"
    
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

class ReviewSchema(Schema):
    class Meta:
        title = "Review"
    
    id = fields.Int(dump_only=True)
    rental_id = fields.Int(dump_only=True)
    instru_ownership_id = fields.Int(dump_only=True)
    renter_id = fields.Int(dump_only=True)
    rating = fields.Int(required=True, validate=lambda x: 1 <= x <= 5)
    comment = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    renter_name = fields.Str(dump_only=True)

class ReviewCreateSchema(Schema):
    class Meta:
        title = "ReviewCreate"
    
    instru_ownership_id = fields.Int(required=True)  # Fixed: was rental_id
    rental_id = fields.Int(required=True)
    rating = fields.Int(required=True, validate=lambda x: 1 <= x <= 5)
    comment = fields.Str(allow_none=True)

class ReviewUpdateSchema(Schema):
    class Meta:
        title = "ReviewUpdate"
    
    rating = fields.Int(validate=lambda x: 1 <= x <= 5)
    comment = fields.Str(allow_none=True)

class ChatMessageSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    session_id = fields.Str(required=True)
    message_type = fields.Str(dump_only=True)  # 'user' or 'assistant'
    content = fields.Str(required=True)
    context_data = fields.Dict(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

class ChatQuerySchema(Schema):
    """Schema for user queries to the chatbot"""
    session_id = fields.Str(required=False, allow_none=True)  # Optional, will be auto-generated if not provided
    message = fields.Str(required=True)

class ChatResponseSchema(Schema):
    """Schema for chatbot responses"""
    session_id = fields.Str()
    user_message = fields.Str()
    assistant_response = fields.Str()
    recommendations = fields.List(fields.Dict())  # List of recommended instruments
    context = fields.Dict()  # Context data used for response
    created_at = fields.DateTime()