from flask import Blueprint, request, jsonify, current_app
from app.services.auth import AuthService
from app.schemas.auth import UserCreateSchema, UserLoginSchema
from app.db.mongo_client import get_db
from app.core.validation_middleware import validate_json
from pydantic import ValidationError

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
@validate_json(UserCreateSchema)
def register_user(data: UserCreateSchema):
    try:
        current_app.logger.info('Register endpoint called')
        auth_service = AuthService(get_db())
        auth_service.register(user_data.model_dump())
        return jsonify({'message': 'user created successfully'}), 201

    except ValidationError as e:
        current_app.logger.error(f'Validation error: {str(e)}')
        return jsonify({'error': 'validation error', 'details': str(e)}), 400

    except Exception as e:
        current_app.logger.error(f'Internal server error: {e}')
        return jsonify({'error': f'internal server error {e}'}), 500

@auth_bp.route('/login', methods=['POST'])
@validate_json(UserLoginSchema)
def login_user(data: UserLoginSchema):
    try:
        current_app.logger.info('Login endpoint called')
        auth_service = AuthService(get_db())
        payload = auth_service.login(data.model_dump())
        return jsonify(payload), 200
    except ValidationError as e:
        current_app.logger.error(f'Validation error: {str(e)}')
        return jsonify({'error': 'validation error', 'details': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f'Internal server error: {e}')
        return jsonify({'error': f'internal server error {e}'}), 500
