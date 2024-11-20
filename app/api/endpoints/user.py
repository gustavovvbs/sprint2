from app.models.user import UserModel
from app.schemas.user import UpdateUser
from app.services.user import UserService 
from app.db.mongo_client import get_db 
from app.core.validation_middleware import validate_json
from flask import Blueprint, request, jsonify, current_app

user_bp = Blueprint('user', __name__)

@user_bp.route('/<user_id>', methods = ['GET'])
def get_user_endpoint(user_id):
    try:
        current_app.logger.info('Get user endpoint called')
        user_service = UserService(get_db())
        user = user_service.get_user_by_id(user_id)
        return jsonify(user), 200
    except ValueError as e:
        current_app.logger.error(f'User not found: {e}')
        return jsonify({'error': 'user not found'}), 404

@user_bp.route('/<user_id>', methods = ['PUT'])
@validate_json(UpdateUser)
def update_user_endpoint(data, user_id):
    try:
        current_app.logger.info('Update user endpoint called')
        user_service = UserService(get_db())
        update_data = data.model_dump()
        result = user_service.update_user(user_id, update_data)
        return jsonify(result), 200
    except ValueError as e:
        current_app.logger.error(f'Error updating user: {e}')
        return jsonify({'error': 'error updating user'}), 400

@user_bp.route('/<user_id>', methods = ['DELETE'])
def delete_user_endpoint(user_id):
    try:
        current_app.logger.info('Delete user endpoint called')
        user_service = UserService(get_db())
        result = user_service.delete_user(user_id)
        return jsonify(result), 200
    except ValueError as e:
        current_app.logger.error(f'Error deleting user: {e}')
        return jsonify({'error': 'error deleting user'}), 404