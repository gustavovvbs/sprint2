from app.services.search import SearchService
from app.schemas.search import PacienteSearch
from app.core.validation_middleware import validate_json
from flask import Blueprint, request, jsonify, current_app

search_bp = Blueprint('search', __name__)

@search_bp.route('/paciente', methods = ['POST'])
@validate_json(PacienteSearch)
def search_paciente(data: PacienteSearch):
    try:
        current_app.logger.info('Search paciente endpoint called')
        search_service = SearchService()
        result = search_service.search_paciente(data)

        return jsonify(result), 200
    except ValueError as e:
        current_app.logger.error(f'Error searching paciente: {e}')
        return jsonify({'error': 'error searching paciente'}), 400