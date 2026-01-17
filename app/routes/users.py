from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.db import db
from app.models import User
from app.schemas import UserSchema, UserUpdateSchema

blp = Blueprint('users', __name__, url_prefix='/api/users', description='User management endpoints')

@blp.route('')
class UserList(MethodView):
    @blp.response(200, UserSchema(many=True))
    @jwt_required()
    def get(self):
        # For now, allow any authenticated user to list users, but in production, add admin check
        users = User.query.all()
        return users

    @blp.arguments(UserSchema)
    @blp.response(201, UserSchema)
    @jwt_required()
    def post(self, user_data):
        # For now, allow any authenticated user to create users, but in production, add admin check
        if User.query.filter_by(email=user_data['email']).first():
            abort(400, message="Email already registered")
        
        user = User(
            email=user_data['email'],
            name=user_data['name'],
            phone=user_data.get('phone'),
            user_type=user_data['user_type']
        )
        user.set_password(user_data['password'])
        
        db.session.add(user)
        db.session.commit()
        return user

@blp.route('/<int:user_id>')
class UserResource(MethodView):
    @blp.response(200, UserSchema)
    @jwt_required()
    def get(self, user_id):
        user = User.query.get_or_404(user_id)
        return user

    @blp.arguments(UserUpdateSchema)
    @blp.response(200, UserSchema)
    @jwt_required()
    def put(self, user_data, user_id):
        user = User.query.get_or_404(user_id)
        for key, value in user_data.items():
            setattr(user, key, value)
        db.session.commit()
        return user

    @blp.response(204)
    @jwt_required()
    def delete(self, user_id):
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()