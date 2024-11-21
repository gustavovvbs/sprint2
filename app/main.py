import logging
from flask import Flask, Blueprint, request, jsonify 
from app.api.endpoints.auth import auth_bp
from app.api.endpoints.user import user_bp
from app.api.endpoints.search import search_bp

from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.register_blueprint(auth_bp, url_prefix = '/auth')
app.register_blueprint(user_bp, url_prefix = '/user')
app.register_blueprint(search_bp, url_prefix = '/search')

logging.basicConfig(level=logging.ERROR)

@app.route('/')
def index():
    return jsonify({'message': 'Hello World'})

