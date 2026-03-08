from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os

# Set default environment early so config.py can use it
if 'FLASK_ENV' not in os.environ:
    os.environ['FLASK_ENV'] = 'development'

from config import config
from database import db

app = Flask(__name__)

# Load configuration
app_env = os.getenv('FLASK_ENV', 'development')
app.config.from_object(config[app_env])

# Initialize extensions
db.init_app(app)

# Initialize CORS with configuration
cors_config = {
    "origins": app.config['CORS_ORIGINS'],
    "methods": app.config['CORS_METHODS'],
    "allow_headers": app.config['CORS_ALLOW_HEADERS'],
    "expose_headers": app.config['CORS_EXPOSE_HEADERS'],
    "supports_credentials": app.config['CORS_SUPPORTS_CREDENTIALS'],
    "max_age": app.config['CORS_MAX_AGE']
}
CORS(app, resources={r"/api/*": cors_config})
jwt = JWTManager(app)

# Import models after db initialization
from models import User, Trip
from routes import auth_bp, trips_bp

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(trips_bp)

# JWT error handlers
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({
        'success': False,
        'error': 'Token has expired'
    }), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        'success': False,
        'error': 'Invalid token'
    }), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        'success': False,
        'error': 'Authorization required. Missing token.'
    }), 401

@app.route('/')
def home():
    return jsonify({"message": "Welcome to EscapeRAI API"})

@app.route('/health')
def health_check():
    try:
        db.session.execute('SELECT 1')
        return jsonify({"status": "healthy", "database": "connected"})
    except Exception as e:
        return jsonify({"status": "unhealthy", "database": "disconnected", "error": str(e)}), 503

if __name__ == '__main__':
    app.run(debug=True)
