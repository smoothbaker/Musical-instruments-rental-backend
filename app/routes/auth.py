from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app.models import db, User
from app.schemas import UserSchema

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/register')
class Register(MethodView):
    @bp.arguments(UserSchema)
    @bp.response(201, UserSchema)
    def post(self, user_data):
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

@bp.route('/login')
class Login(MethodView):
    @bp.arguments(UserSchema(only=('email', 'password')))
    @bp.response(200)
    def post(self, user_data):
        user = User.query.filter_by(email=user_data['email']).first()
        
        if not user or not user.check_password(user_data['password']):
            abort(401, message="Invalid credentials")
        
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'user_type': user.user_type
            }
        }
#to refresh access token
@bp.route('/refresh')
class Refresh(MethodView):
    @bp.response(200)
    @jwt_required(refresh=True)
    def post(self):
        current_user_id = get_jwt_identity()
        access_token = create_access_token(identity=current_user_id)
        return {'access_token': access_token}

@bp.route('/profile')
class Profile(MethodView):
    @bp.response(200, UserSchema)
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        return user