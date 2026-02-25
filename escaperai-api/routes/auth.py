"""
Example authentication routes demonstrating JWT token generation and validation.
This shows how to implement login, token refresh, and protected endpoints.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from database import db
from models import User
from utils import (
    hash_password,
    verify_password,
    validate_password_strength,
    validate_email,
    is_disposable_email,
    normalize_email,
    generate_tokens,
    generate_access_token,
    create_token_response,
    get_user_from_token,
    get_token_claims,
)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user.
    
    Request body:
    {
        "email": "user@example.com",
        "password": "MyP@ssw0rd123"
    }
    
    Response:
    {
        "success": true,
        "message": "User registered successfully",
        "data": {
            "user_id": 1,
            "email": "user@example.com"
        }
    }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'error': 'Request body is required'}), 400
    
    email = data.get('email', '').strip()
    password = data.get('password', '')
    
    # Validate email format
    email_validation = validate_email(email, strict=True)
    if not email_validation['valid']:
        return jsonify({
            'success': False,
            'error': 'Invalid email format',
            'details': email_validation['errors']
        }), 400
    
    # Normalize email
    email = normalize_email(email)
    
    # Check for disposable email
    if is_disposable_email(email):
        return jsonify({
            'success': False,
            'error': 'Disposable email addresses are not allowed'
        }), 400
    
    # Validate password strength
    strength_validation = validate_password_strength(password)
    if not strength_validation['valid']:
        return jsonify({
            'success': False,
            'error': 'Password does not meet requirements',
            'details': strength_validation['errors']
        }), 400
    
    # Check if user exists
    if User.query.filter_by(email=email).first():
        return jsonify({'success': False, 'error': 'Email already registered'}), 409
    
    # Create new user
    try:
        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'data': {
                'user_id': user.id,
                'email': user.email
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate user and return JWT tokens.
    
    Request body:
    {
        "email": "user@example.com",
        "password": "MyP@ssw0rd123"
    }
    
    Response:
    {
        "success": true,
        "data": {
            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
            "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
            "token_type": "Bearer",
            "expires_in": 3600
        }
    }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'error': 'Request body is required'}), 400
    
    email = data.get('email', '').strip()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'success': False, 'error': 'Email and password are required'}), 400
    
    # Validate email format
    email_validation = validate_email(email, strict=False)
    if not email_validation['valid']:
        return jsonify({
            'success': False,
            'error': 'Invalid email format',
            'details': email_validation['errors']
        }), 400
    
    # Normalize email
    email = normalize_email(email)
    
    # Find user
    user = User.query.filter_by(email=email).first()
    
    if not user or not user.check_password(password):
        return jsonify({'success': False, 'error': 'Invalid email or password'}), 401
    
    # Generate tokens
    additional_claims = {'email': user.email}
    response, status_code = create_token_response(user.id, additional_claims, 200)
    
    return jsonify(response), status_code


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Generate a new access token using the refresh token.
    
    Headers:
    Authorization: Bearer <refresh_token>
    
    Response:
    {
        "success": true,
        "data": {
            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
            "token_type": "Bearer",
            "expires_in": 3600
        }
    }
    """
    user_id = get_user_from_token()
    claims = get_token_claims()
    
    # Generate new access token
    additional_claims = {k: v for k, v in claims.items() if k != 'exp' and k != 'iat'}
    new_access_token = generate_access_token(user_id, additional_claims)
    
    from config import config
    import os
    app_env = os.getenv('FLASK_ENV', 'development')
    access_token_expires = config[app_env].JWT_ACCESS_TOKEN_EXPIRES
    
    return jsonify({
        'success': True,
        'data': {
            'access_token': new_access_token,
            'token_type': 'Bearer',
            'expires_in': access_token_expires
        }
    }), 200


@auth_bp.route('/verify', methods=['GET'])
@jwt_required()
def verify_token():
    """
    Verify the current JWT token and return user information.
    
    Headers:
    Authorization: Bearer <access_token>
    
    Response:
    {
        "success": true,
        "data": {
            "user_id": 1,
            "email": "user@example.com",
            "token_claims": { ... }
        }
    }
    """
    user_id = get_user_from_token()
    claims = get_token_claims()
    
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404
    
    return jsonify({
        'success': True,
        'data': {
            'user_id': user_id,
            'email': user.email,
            'token_claims': claims
        }
    }), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Logout the current user (token revocation stub).
    
    Headers:
    Authorization: Bearer <access_token>
    
    Response:
    {
        "success": true,
        "message": "Logged out successfully"
    }
    
    Note: For production, implement token blacklisting with Redis or database.
    """
    # TODO: Implement token revocation if needed
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Get the current authenticated user's profile.
    
    Headers:
    Authorization: Bearer <access_token>
    
    Response:
    {
        "success": true,
        "data": {
            "id": 1,
            "email": "user@example.com",
            "created_at": "2024-02-25T10:30:00+00:00",
            "updated_at": "2024-02-25T10:30:00+00:00",
            "trips_count": 3
        }
    }
    """
    user_id = get_user_from_token()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404
    
    return jsonify({
        'success': True,
        'data': user.to_dict()
    }), 200
