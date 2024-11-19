from flask import Blueprint, request, jsonify 
from app.services.auth import AuthService
from app.schemas.auth import UserCreateSchema, UserLoginSchema
from app.db.mongo_client import get_db
from pydantic import ValidationError

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register_user():
    try:
        auth_service = AuthService(get_db())
        user_data = UserCreateSchema(**request.json)
        auth_service.register(user_data.dict())
        return jsonify({'message': 'user created successfully'}), 201

    except ValidationError as e:
        return jsonify({'error': 'validation error', 'details': str(e)}), 400

    except Exception as e:
        return jsonify({'error': f'internal server error {e}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login_user():
    try:
        auth_service = AuthService(get_db())
        user_data = UserLoginSchema(**request.json)
        payload = auth_service.login(user_data.email, user_data.password)
        return jsonify(payload), 200
    except ValidationError as e:
        return jsonify({'error': 'validation error', 'details': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'internal server error {e}'}), 500
