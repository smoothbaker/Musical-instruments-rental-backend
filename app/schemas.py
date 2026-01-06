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