"""
Authentication middleware for protecting routes.
Provides decorators for JWT authentication, role-based access control, and permission checking.
"""

from functools import wraps
from flask import request, jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, verify_jwt_in_request
from typing import Optional, Callable, List


def auth_required(f: Callable) -> Callable:
    """
    Decorator to require JWT authentication on a route.
    
    Use this decorator when you want a route to require a valid JWT token.
    The authenticated user ID will be available via get_jwt_identity().
    
    Example:
        @app.route('/api/profile')
        @auth_required
        def get_profile():
            user_id = g.user_id
            return jsonify({'user_id': user_id})
    
    Returns:
        401 if token is missing, invalid, or expired
    """
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        # Store user_id in g for easy access throughout the request
        # Convert from string (JWT spec) back to int for database queries
        user_id_str = get_jwt_identity()
        g.user_id = int(user_id_str)
        g.jwt = get_jwt()
        return f(*args, **kwargs)
    
    return decorated_function


def auth_optional(f: Callable) -> Callable:
    """
    Decorator to optionally authenticate a route.
    
    Use when a route can work with or without authentication.
    The authenticated user ID will be available via g.user_id (or None if not authenticated).
    
    Example:
        @app.route('/api/posts')
        @auth_optional
        def get_posts():
            # If user is authenticated, g.user_id is set
            # If not, g.user_id is None
            if g.user_id:
                posts = Post.query.filter_by(user_id=g.user_id).all()
            else:
                posts = Post.query.filter_by(public=True).all()
            return jsonify([p.to_dict() for p in posts])
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Attempt to verify JWT, but don't fail if missing
        try:
            verify_jwt_in_request(optional=True)
            user_id_str = get_jwt_identity()
            # Convert from string (JWT spec) back to int for database queries
            g.user_id = int(user_id_str) if user_id_str else None
            g.jwt = get_jwt() if g.user_id else {}
        except Exception:
            g.user_id = None
            g.jwt = {}
        
        return f(*args, **kwargs)
    
    return decorated_function


def owner_only(resource_id_param: str = 'id') -> Callable:
    """
    Decorator to ensure user owns the resource they're accessing.
    
    Checks that the resource's user_id matches the authenticated user's ID.
    Requires a function that returns the resource object given the resource ID.
    
    Args:
        resource_id_param (str): Name of the URL parameter containing the resource ID
    
    Example:
        @app.route('/api/trips/<int:id>', methods=['PUT'])
        @owner_only('id')
        def update_trip(id):
            # This route will only execute if the trip belongs to the current user
            trip = Trip.query.get(id)
            return jsonify(trip.to_dict())
    
    Returns:
        401 if not authenticated
        403 if user doesn't own the resource
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            user_id_str = get_jwt_identity()
            # Convert from string (JWT spec) back to int for database queries
            g.user_id = int(user_id_str)
            g.jwt = get_jwt()
            
            # Get resource ID from URL parameters
            resource_id = kwargs.get(resource_id_param)
            
            if resource_id is None:
                return jsonify({
                    'success': False,
                    'error': f'Resource ID parameter "{resource_id_param}" not found'
                }), 400
            
            # Import here to avoid circular imports
            from models import Trip, User
            
            # Determine which model to check based on route/function name
            resource_model = _get_resource_model(f.__name__)
            
            if resource_model is None:
                return jsonify({
                    'success': False,
                    'error': 'Could not determine resource type'
                }), 500
            
            # Get the resource
            resource = resource_model.query.get(resource_id)
            
            if not resource:
                return jsonify({
                    'success': False,
                    'error': 'Resource not found'
                }), 404
            
            # Check if user owns it
            if not hasattr(resource, 'user_id'):
                return jsonify({
                    'success': False,
                    'error': 'Resource type does not support ownership check'
                }), 500
            
            if resource.user_id != user_id:
                return jsonify({
                    'success': False,
                    'error': 'Access denied. You do not own this resource.'
                }), 403
            
            # Store resource in g for use in the route
            g.resource = resource
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator




def rate_limit(max_requests: int = 100, window_seconds: int = 3600) -> Callable:
    """
    Decorator to implement rate limiting on a route.
    
    Note: This requires Redis for production use.
    Currently uses in-memory storage suitable for development/testing.
    
    Args:
        max_requests (int): Maximum requests allowed in window (default: 100)
        window_seconds (int): Time window in seconds (default: 3600 = 1 hour)
    
    Example:
        @app.route('/api/trips')
        @auth_required
        @rate_limit(max_requests=10, window_seconds=60)
        def get_trips():
            # Max 10 requests per minute
            trips = Trip.query.filter_by(user_id=g.user_id).all()
            return jsonify([t.to_dict() for t in trips])
    
    Returns:
        429 if rate limit exceeded
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get client identifier (user_id if authenticated, IP if not)
            try:
                client_id = f"user_{get_jwt_identity()}"
            except Exception:
                client_id = f"ip_{request.remote_addr}"
            
            # In-memory rate limit tracker (use Redis in production)
            if not hasattr(g, 'rate_limit_tracker'):
                g.rate_limit_tracker = {}
            
            current_time = __import__('time').time()
            tracker_key = f"{client_id}:{f.__name__}"
            
            # Clean old requests outside the window
            if tracker_key in g.rate_limit_tracker:
                g.rate_limit_tracker[tracker_key] = [
                    req_time for req_time in g.rate_limit_tracker[tracker_key]
                    if current_time - req_time < window_seconds
                ]
            else:
                g.rate_limit_tracker[tracker_key] = []
            
            # Check rate limit
            if len(g.rate_limit_tracker[tracker_key]) >= max_requests:
                return jsonify({
                    'success': False,
                    'error': 'Rate limit exceeded',
                    'retry_after': window_seconds
                }), 429
            
            # Record this request
            g.rate_limit_tracker[tracker_key].append(current_time)
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator


def validate_json(*required_fields: str) -> Callable:
    """
    Decorator to validate required JSON fields in request body.
    
    Args:
        *required_fields: Field names that must be present in JSON body
    
    Example:
        @app.route('/api/trips', methods=['POST'])
        @auth_required
        @validate_json('destination', 'start_date', 'end_date')
        def create_trip():
            data = request.get_json()
            # All required fields are guaranteed to be present
            return jsonify(trip.to_dict())
    
    Returns:
        400 if required fields are missing
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({
                    'success': False,
                    'error': 'Request must be JSON'
                }), 400
            
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'Request body is required'
                }), 400
            
            # Check required fields
            missing_fields = [f for f in required_fields if f not in data or data[f] is None]
            
            if missing_fields:
                return jsonify({
                    'success': False,
                    'error': 'Missing required fields',
                    'missing': missing_fields
                }), 400
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator


def _get_resource_model(function_name: str):
    """
    Determine the resource model based on function name.
    
    Internal helper for owner_only decorator.
    """
    function_name = function_name.lower()
    
    from models import Trip, User
    
    if 'trip' in function_name:
        return Trip
    elif 'user' in function_name:
        return User
    
    return None


# Convenience variable for combining decorators
def protect(f: Callable) -> Callable:
    """
    Alias for auth_required.
    Shorter name for common use case.
    
    Example:
        @app.route('/api/secure')
        @protect
        def secure_endpoint():
            return jsonify({'message': 'authenticated'})
    """
    return auth_required(f)
