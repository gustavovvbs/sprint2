from flask import Flask, Blueprint, request, jsonify 
from app.api.endpoints.auth import auth_bp

app = Flask(__name__)
app.register_blueprint(auth_bp, url_prefix = '/auth')

@app.route('/')
def index():
    return jsonify({'message': 'Hello World'})

