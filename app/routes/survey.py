from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import SurveyResponse, User, db
from app.schemas import SurveyResponseSchema, SurveyResponseUpdateSchema

bp = Blueprint('survey', __name__, url_prefix='/api/survey')

@bp.route('')
class SurveyList(MethodView):
    @bp.response(200, SurveyResponseSchema)
    @jwt_required()
    def get(self):
        """Get current user's survey response"""
        user_id = int(get_jwt_identity())
        user = User.query.get_or_404(user_id)
        
        survey = SurveyResponse.query.filter_by(user_id=user_id).first()
        if not survey:
            abort(404, message="Survey not found for this user")
        
        return survey

    @bp.arguments(SurveyResponseSchema)
    @bp.response(201, SurveyResponseSchema)
    @jwt_required()
    def post(self, survey_data):
        """Create survey response after user registration"""
        user_id = int(get_jwt_identity())
        user = User.query.get_or_404(user_id)
        
        # Check if survey already exists
        existing_survey = SurveyResponse.query.filter_by(user_id=user_id).first()
        if existing_survey:
            abort(400, message="Survey response already exists for this user")
        
        # Only renters should fill surveys
        if user.user_type != 'renter':
            abort(403, message="Only renters can fill the survey")
        
        survey = SurveyResponse(user_id=user_id, **survey_data)
        db.session.add(survey)
        db.session.commit()
        
        return survey, 201

@bp.route('/<int:survey_id>')
class SurveyDetail(MethodView):
    @bp.response(200, SurveyResponseSchema)
    @jwt_required()
    def get(self, survey_id):
        """Get survey response by ID"""
        user_id = int(get_jwt_identity())
        survey = SurveyResponse.query.get_or_404(survey_id)
        
        # Users can only view their own survey
        if survey.user_id != user_id:
            abort(403, message="Unauthorized")
        
        return survey

    @bp.arguments(SurveyResponseUpdateSchema)
    @bp.response(200, SurveyResponseSchema)
    @jwt_required()
    def put(self, update_data, survey_id):
        """Update survey response"""
        user_id = int(get_jwt_identity())
        survey = SurveyResponse.query.get_or_404(survey_id)
        
        # Users can only update their own survey
        if survey.user_id != user_id:
            abort(403, message="Unauthorized")
        
        for key, value in update_data.items():
            setattr(survey, key, value)
        
        db.session.commit()
        return survey

    @bp.response(204)
    @jwt_required()
    def delete(self, survey_id):
        """Delete survey response"""
        user_id = int(get_jwt_identity())
        survey = SurveyResponse.query.get_or_404(survey_id)
        
        # Users can only delete their own survey
        if survey.user_id != user_id:
            abort(403, message="Unauthorized")
        
        db.session.delete(survey)
        db.session.commit()
