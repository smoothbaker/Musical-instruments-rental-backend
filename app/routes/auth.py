from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app.models import db, User, SurveyResponse
from app.schemas import UserSchema

blp = Blueprint('auth', __name__, url_prefix='/api/auth', description='Authentication endpoints')

@blp.route('/register')
class Register(MethodView):
    @blp.arguments(UserSchema)
    @blp.response(201, UserSchema)
    def post(self, user_data):
        """Register a new user
        
        Create a new user account with email, password, and user type.
        Returns the created user object.
        """
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
        db.session.flush()  # Flush to get the user ID without committing
        
        # If user is a renter and survey data is provided in headers/body, create survey response
        # The survey will be submitted separately via POST /api/survey
        
        db.session.commit()
        return user

@blp.route('/login')
class Login(MethodView):
    @blp.arguments(UserSchema(only=('email', 'password')))
    @blp.response(200)
    def post(self, user_data):
        """User login
        
        Authenticate user with email and password.
        Returns JWT access and refresh tokens.
        """
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

@blp.route('/refresh')
class Refresh(MethodView):
    @blp.response(200)
    @jwt_required(refresh=True)
    def post(self):
        """Refresh access token
        
        Use refresh token to obtain a new access token.
        Requires valid refresh token in Authorization header.
        """
        current_user_id = get_jwt_identity()
        access_token = create_access_token(identity=current_user_id)
        return {'access_token': access_token}

@blp.route('/profile')
class Profile(MethodView):
    @blp.response(200, UserSchema)
    @jwt_required()
    def get(self):
        """Get user profile
        
        Retrieve the profile of the currently authenticated user.
        Requires valid access token in Authorization header.
        """
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        return user