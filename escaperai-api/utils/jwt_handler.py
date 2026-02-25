"""
JWT token generation and validation utilities for authentication.
Uses flask-jwt-extended for secure token handling.
"""

from datetime import datetime, timedelta, timezone
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_jwt_identity,
    get_jwt,
)
from functools import wraps
from flask import current_app, jsonify


def generate_tokens(user_id, additional_claims=None):
    """
    Generate access and refresh JWT tokens for a user.
    
    Args:
        user_id (int): The user ID to encode in the token
        additional_claims (dict): Optional additional claims to include in tokens
        
    Returns:
        dict: {
            'access_token': str,
            'refresh_token': str,
            'token_type': 'Bearer',
            'expires_in': int (seconds)
        }
    """
    # Convert user_id to string - JWT spec requires 'sub' to be a string
    user_id_str = str(user_id)
    claims = additional_claims or {}
    claims['sub'] = user_id_str
    
    access_token = create_access_token(
        identity=user_id_str,
        additional_claims=claims
    )
    
    refresh_token = create_refresh_token(
        identity=user_id_str,
        additional_claims=claims
    )
    
    access_token_expires = current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', 3600)
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'Bearer',
        'expires_in': access_token_expires
    }


def generate_access_token(user_id, additional_claims=None, expires_in=None):
    """
    Generate only an access token for a user.
    
    Args:
        user_id (int): The user ID to encode in the token
        additional_claims (dict): Optional additional claims to include in token
        expires_in (int): Token expiration time in seconds (uses config default if None)
        
    Returns:
        str: The JWT access token
    """
    # Convert user_id to string - JWT spec requires 'sub' to be a string
    user_id_str = str(user_id)
    claims = additional_claims or {}
    claims['sub'] = user_id_str
    
    if expires_in:
        expires_delta = timedelta(seconds=expires_in)
        return create_access_token(
            identity=user_id_str,
            additional_claims=claims,
            expires_delta=expires_delta
        )
    else:
        return create_access_token(identity=user_id_str, additional_claims=claims)


def generate_refresh_token(user_id, additional_claims=None):
    """
    Generate a refresh token for a user.
    
    Args:
        user_id (int): The user ID to encode in the token
        additional_claims (dict): Optional additional claims to include in token
        
    Returns:
        str: The JWT refresh token
    """
    # Convert user_id to string - JWT spec requires 'sub' to be a string
    user_id_str = str(user_id)
    claims = additional_claims or {}
    claims['sub'] = user_id_str
    
    return create_refresh_token(identity=user_id_str, additional_claims=claims)


def verify_token(token, refresh=False):
    """
    Verify and decode a JWT token.
    
    Args:
        token (str): The JWT token to verify
        refresh (bool): If True, verify as refresh token; if False, verify as access token
        
    Returns:
        dict: The decoded token claims if valid, None if invalid
        
    Raises:
        Exception: JWT-related errors (expired, invalid signature, etc.)
    """
    try:
        decoded_token = decode_token(token)
        return decoded_token
    except Exception as e:
        raise Exception(f"Token verification failed: {str(e)}")


def get_user_from_token():
    """
    Get the current user ID from the JWT token in the request.
    
    Use this inside a route protected with @jwt_required()
    
    Returns:
        int: The user ID from the token (converted from string JWT spec)
    """
    user_id_str = get_jwt_identity()
    return int(user_id_str) if user_id_str else None


def get_token_claims():
    """
    Get all claims from the current JWT token.
    
    Use this inside a route protected with @jwt_required()
    
    Returns:
        dict: All claims in the current token
    """
    return get_jwt()


def get_token_expiration(token):
    """
    Get the expiration time of a JWT token.
    
    Args:
        token (str): The JWT token to check
        
    Returns:
        datetime: The expiration datetime in UTC, or None if token is invalid
    """
    try:
        decoded = decode_token(token)
        exp_timestamp = decoded.get('exp')
        if exp_timestamp:
            return datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        return None
    except Exception:
        return None


def is_token_expired(token):
    """
    Check if a JWT token is expired.
    
    Args:
        token (str): The JWT token to check
        
    Returns:
        bool: True if token is expired or invalid, False if valid
    """
    try:
        exp_time = get_token_expiration(token)
        if exp_time is None:
            return True
        return datetime.now(timezone.utc) > exp_time
    except Exception:
        return True


def get_token_age(token):
    """
    Get the age of a JWT token (how long it has been valid).
    
    Args:
        token (str): The JWT token to check
        
    Returns:
        int: Age in seconds, or None if token is invalid
    """
    try:
        decoded = decode_token(token)
        issued_at = decoded.get('iat')
        if issued_at:
            return int(datetime.now(timezone.utc).timestamp()) - issued_at
        return None
    except Exception:
        return None


def get_token_remaining_time(token):
    """
    Get the remaining time until a JWT token expires.
    
    Args:
        token (str): The JWT token to check
        
    Returns:
        int: Remaining time in seconds, or 0 if expired, None if invalid
    """
    try:
        exp_time = get_token_expiration(token)
        if exp_time is None:
            return None
        remaining = (exp_time - datetime.now(timezone.utc)).total_seconds()
        return max(0, int(remaining))
    except Exception:
        return None


def create_token_response(user_id, additional_claims=None, status_code=200):
    """
    Create a JSON response with access and refresh tokens.
    
    Typical usage in a login route:
    ```python
    @app.route('/login', methods=['POST'])
    def login():
        # ... validate credentials ...
        return create_token_response(user.id, {'email': user.email})
    ```
    
    Args:
        user_id (int): The user ID to encode in tokens
        additional_claims (dict): Additional claims to include
        status_code (int): HTTP status code for response
        
    Returns:
        tuple: (response_dict, status_code)
    """
    tokens = generate_tokens(user_id, additional_claims)
    return {
        'success': True,
        'data': tokens
    }, status_code
