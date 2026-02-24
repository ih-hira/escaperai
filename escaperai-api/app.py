from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
from config import config

app = Flask(__name__)

# Load configuration
app_env = os.getenv('FLASK_ENV', 'development')
app.config.from_object(config[app_env])

# Initialize extensions
db = SQLAlchemy(app)
CORS(app)

# Import models after db initialization
from models import User, Trip

@app.route('/')
def home():
    return jsonify({"message": "Welcome to EscaperAi API"})

@app.route('/health')
def health_check():
    try:
        db.session.execute('SELECT 1')
        return jsonify({"status": "healthy", "database": "connected"})
    except Exception as e:
        return jsonify({"status": "unhealthy", "database": "disconnected", "error": str(e)}), 503

if __name__ == '__main__':
    app.run(debug=True)
