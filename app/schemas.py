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
    condition = fields.Str()
    daily_rate = fields.Float(required=True)
    description = fields.Str()
    image_url = fields.Str()
    location = fields.Str()
    is_available = fields.Bool(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

class RentalSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    instrument_id = fields.Int(required=True)
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    actual_return_date = fields.Date()
    total_cost = fields.Float(dump_only=True)
    status = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

class ReviewSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    instrument_id = fields.Int(required=True)
    rating = fields.Int(required=True, validate=lambda x: 1 <= x <= 5)
    comment = fields.Str()
    created_at = fields.DateTime(dump_only=True)