# Authentication Middleware Documentation

## Overview

The authentication middleware provides a set of decorators for protecting routes and enforcing security policies. These decorators work seamlessly with Flask-JWT-Extended to provide flexible, composable authentication and authorization.

## Core Decorators

### 1. @auth_required

Requires a valid JWT token to access the route.

**Usage:**
```python
from utils import auth_required
from flask import g

@app.route('/api/profile')
@auth_required
def get_profile():
    user_id = g.user_id  # User ID extracted from token
    jwt_claims = g.jwt    # All JWT claims
    return jsonify({'user_id': user_id})
```

**Returns:**
- 401 if token is missing, invalid, or expired

**Available in route:**
- `g.user_id` - The authenticated user's ID
- `g.jwt` - The JWT claims dictionary

### 2. @auth_optional

Allows a route to work with or without authentication.

**Usage:**
```python
from utils import auth_optional
from flask import g

@app.route('/api/public-posts')
@auth_optional
def get_posts():
    if g.user_id:
        # User is authenticated
        posts = Post.query.filter_by(user_id=g.user_id).all()
    else:
        # User is not authenticated
        posts = Post.query.filter_by(public=True).all()
    
    return jsonify([p.to_dict() for p in posts])
```

**Returns:**
- Always succeeds (no error if token missing)

**Available in route:**
- `g.user_id` - User ID if authenticated, None otherwise
- `g.jwt` - JWT claims if authenticated, empty dict otherwise

### 3. @owner_only(resource_id_param)

Ensures the user owns the resource they're accessing.

**Usage:**
```python
from utils import owner_only
from flask import g

@app.route('/api/trips/<int:id>')
@owner_only('id')
def get_trip(id):
    # Only executes if current user owns the trip with this ID
    trip = g.resource  # The resource is automatically loaded
    return jsonify(trip.to_dict())

@app.route('/api/trips/<int:id>', methods=['PUT'])
@owner_only('id')
def update_trip(id):
    trip = g.resource
    # ... update logic ...
    return jsonify(trip.to_dict())
```

**Parameters:**
- `resource_id_param` (str): Name of the URL parameter containing the resource ID

**Returns:**
- 401 if not authenticated
- 403 if user doesn't own the resource
- 404 if resource doesn't exist

**Available in route:**
- `g.user_id` - The authenticated user's ID
- `g.resource` - The loaded resource object
- `g.jwt` - The JWT claims

**Detection:**
- Automatically detects resource type from function name ('trip', 'user', etc.)
- Checks `resource.user_id == current_user_id`

### 4. @role_required(role_name)

Restricts access to users with specific roles.

**Usage:**
```python
from utils import role_required

@app.route('/api/admin/users')
@role_required('admin')
def list_all_users():
    # Only admin users can access this
    users = User.query.all()
    return jsonify([u.to_dict() for u in users])

@app.route('/api/moderate/reports')
@role_required('moderator')
def list_reports():
    # Only moderators can access this
    reports = Report.query.all()
    return jsonify([r.to_dict() for r in reports])
```

**Parameters:**
- `role_name` (str): Required role name

**Returns:**
- 401 if not authenticated
- 403 if user doesn't have required role

**Note:** Requires implementing `role` field in User model. Currently a template for future role implementation.

### 5. @permission_required(*permissions)

Restricts access to users with specific permissions.

**Usage:**
```python
from utils import permission_required

@app.route('/api/trips', methods=['POST'])
@permission_required('write:trips')
def create_trip():
    # Only users with 'write:trips' permission
    return jsonify({'success': True})

@app.route('/api/trips/<int:id>/publish', methods=['PUT'])
@permission_required('write:trips', 'publish:trips')
def publish_trip(id):
    # Requires both permissions
    return jsonify({'success': True})
```

**Parameters:**
- `*permissions` (str): One or more permission strings

**Returns:**
- 401 if not authenticated
- 403 if user missing required permissions
- Response includes list of missing permissions

**Note:** Requires implementing `permissions` field in User model. Currently a template for future permission implementation.

### 6. @rate_limit(max_requests, window_seconds)

Rate limits a route to prevent abuse.

**Usage:**
```python
from utils import rate_limit, auth_required

@app.route('/api/trips')
@auth_required
@rate_limit(max_requests=30, window_seconds=60)
def list_trips():
    # Max 30 requests per minute
    trips = Trip.query.all()
    return jsonify([t.to_dict() for t in trips])

@app.route('/api/search', methods=['POST'])
@rate_limit(max_requests=5, window_seconds=60)
def search():
    # Max 5 requests per minute (no auth needed)
    return jsonify({'results': []})
```

**Parameters:**
- `max_requests` (int): Maximum requests allowed in window (default: 100)
- `window_seconds` (int): Time window in seconds (default: 3600)

**Returns:**
- 429 if rate limit exceeded
- Response includes `retry_after` field

**Tracking:**
- Authenticated users: Tracked by user ID
- Unauthenticated users: Tracked by IP address
- Per-route tracking (unique per endpoint)

**Note:** Current implementation uses in-memory storage, suitable for development/single-instance deployments. For production multi-instance deployments, integrate with Redis.

### 7. @validate_json(*required_fields)

Validates that required JSON fields are present in request body.

**Usage:**
```python
from utils import validate_json, auth_required

@app.route('/api/trips', methods=['POST'])
@auth_required
@validate_json('destination', 'start_date', 'end_date')
def create_trip():
    # Guaranteed to have destination, start_date, end_date
    data = request.get_json()
    return jsonify({'success': True})

@app.route('/api/trips/<int:id>', methods=['PUT'])
@validate_json('destination', 'start_date')
def update_trip(id):
    # Only destination and start_date are required
    data = request.get_json()
    return jsonify({'success': True})
```

**Parameters:**
- `*required_fields` (str): Field names that must be present and non-null

**Returns:**
- 400 if request is not JSON
- 400 if request body is empty
- 400 if required fields are missing/null
- Response includes list of missing fields

## Composition Patterns

Decorators can be stacked to create complex protection schemes:

### Pattern 1: Authentication + Validation

```python
@app.route('/api/trips', methods=['POST'])
@auth_required
@validate_json('destination', 'start_date', 'end_date')
def create_trip():
    data = request.get_json()
    user_id = g.user_id
    # Create trip...
    return jsonify(trip.to_dict()), 201
```

### Pattern 2: Authentication + Ownership + Validation

```python
@app.route('/api/trips/<int:id>', methods=['PUT'])
@auth_required
@validate_json('destination', 'start_date')
def update_trip(id):
    user_id = g.user_id
    trip = Trip.query.get(id)
    
    if trip.user_id != user_id:
        return error('Access denied'), 403
    
    # Update trip...
    return jsonify(trip.to_dict()), 200
```

### Pattern 3: Authentication + Rate Limiting

```python
@app.route('/api/search', methods=['POST'])
@auth_required
@rate_limit(max_requests=10, window_seconds=60)
def search():
    user_id = g.user_id
    # Expensive search operation...
    return jsonify(results), 200
```

### Pattern 4: Optional Auth + Validation

```python
@app.route('/api/posts')
@auth_optional
@validate_json('content')
def create_post():
    data = request.get_json()
    
    if g.user_id:
        # Create authenticated post
        post = Post(user_id=g.user_id, content=data['content'])
    else:
        # Create anonymous post
        post = Post(content=data['content'], anonymous=True)
    
    return jsonify(post.to_dict()), 201
```

## Request Context Variables

All decorators populate the Flask `g` object with useful data:

### When authenticated:

```python
g.user_id    # int - The authenticated user's ID
g.jwt        # dict - All JWT claims from the token

# Example JWT claims:
{
    'sub': 123,           # Subject (user ID)
    'exp': 1234567890,    # Expiration timestamp
    'iat': 1234567800,    # Issued at timestamp
    'email': 'user@example.com',  # Additional claims
    'jti': 'token-id'     # JWT ID for blacklisting
}
```

### When not authenticated (auth_optional):

```python
g.user_id    # None
g.jwt        # {}
```

## Error Responses

All middleware returns standardized error responses:

### 401 Unauthorized (Missing/Invalid Token)

```json
{
    "success": false,
    "error": "Authorization required. Missing token."
}
```

### 403 Forbidden (Access Denied)

```json
{
    "success": false,
    "error": "Access denied. You do not own this resource."
}
```

### 404 Not Found (Resource)

```json
{
    "success": false,
    "error": "Resource not found"
}
```

### 429 Too Many Requests (Rate Limit)

```json
{
    "success": false,
    "error": "Rate limit exceeded",
    "retry_after": 60
}
```

### 400 Bad Request (Validation)

```json
{
    "success": false,
    "error": "Missing required fields",
    "missing": ["destination", "start_date"]
}
```

## Best Practices

### 1. Order of Decorators Matters

Place more specific decorators closer to the function:

```python
# Good - Validation is checked before business logic
@app.route('/api/data', methods=['POST'])
@auth_required           # General auth first
@validate_json('field')  # Specific validation second
def handle_data():
    pass

# Less efficient - Validation happens after auth check
@app.route('/api/data', methods=['POST'])
@validate_json('field')
@auth_required
def handle_data():
    pass
```

### 2. Combine Related Decorators

```python
# Good - Resource ownership + auth together
@app.route('/api/trips/<int:id>', methods=['PUT'])
@auth_required
def update_trip(id):
    trip = Trip.query.get(id)
    if trip.user_id != g.user_id:
        return error('Access denied'), 403
    # ...

# Or with ownership check built in
@app.route('/api/trips/<int:id>', methods=['PUT'])
@owner_only('id')
def update_trip(id):
    trip = g.resource
    # ...
```

### 3. Use auth_optional for Public/Private Routes

```python
@app.route('/api/profile/<int:user_id>')
@auth_optional
def get_profile(user_id):
    if g.user_id == user_id:
        # User viewing their own profile - show private info
        user = User.query.get(user_id)
        return jsonify(user.to_detailed_dict())
    else:
        # User viewing someone else's profile - show public info
        user = User.query.get(user_id)
        return jsonify(user.to_public_dict())
```

### 4. Implement Role/Permission Checking

```python
# For admin-only endpoints
@app.route('/api/admin/dashboard')
@role_required('admin')
def admin_dashboard():
    # Only admin role can access
    pass

# For permission-based access
@app.route('/api/posts', methods=['POST'])
@permission_required('create:posts')
def create_post():
    # Only users with create:posts permission
    pass
```

### 5. Rate Limit Expensive Operations

```python
@app.route('/api/generate-itinerary', methods=['POST'])
@auth_required
@rate_limit(max_requests=5, window_seconds=3600)  # 5 per hour
@validate_json('destination', 'dates')
def generate_itinerary():
    # This AI operation is expensive, rate limit it
    pass
```

## Production Considerations

### 1. Token Blacklisting

Implement token revocation for logout:

```python
from datetime import datetime, timezone
# In logout endpoint:
@app.route('/api/auth/logout', methods=['POST'])
@auth_required
def logout():
    jti = g.jwt['jti']
    exp = datetime.fromtimestamp(g.jwt['exp'], tz=timezone.utc)
    
    # Add to Redis blacklist
    redis.setex(f"token_blacklist:{jti}", exp, "revoked")
    
    return jsonify({'success': True})
```

### 2. Redis Rate Limiting

For production multi-instance deployments:

```python
import redis
from redis import Redis

redis_client = redis.Redis(host='localhost', port=6379)

def rate_limit_redis(max_requests, window_seconds):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                client_id = f"user_{get_jwt_identity()}"
            except:
                client_id = f"ip_{request.remote_addr}"
            
            key = f"rate_limit:{client_id}:{f.__name__}"
            current = redis_client.incr(key)
            
            if current == 1:
                redis_client.expire(key, window_seconds)
            
            if current > max_requests:
                return jsonify({'error': 'Rate limit exceeded'}), 429
            
            return f(*args, **kwargs)
        return decorated
    return decorator
```

### 3. Audit Logging

Log all sensitive operations:

```python
import logging

audit_logger = logging.getLogger('audit')

@app.route('/api/data/<int:id>', methods=['DELETE'])
@auth_required
def delete_data(id):
    user_id = g.user_id
    audit_logger.info(f"DELETE data/{id} by user {user_id}")
    # ... delete logic ...
```

## Testing

Example test for protected routes:

```python
import pytest
from app import app, db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

def test_protected_route_requires_auth(client):
    response = client.get('/api/trips')
    assert response.status_code == 401

def test_protected_route_with_auth(client, auth_token):
    response = client.get('/api/trips',
        headers={'Authorization': f'Bearer {auth_token}'})
    assert response.status_code == 200
```

## Summary

| Decorator | Purpose | Returns | Use Case |
|-----------|---------|---------|----------|
| `@auth_required` | Require JWT | 401 if missing | Protected endpoints |
| `@auth_optional` | Optional JWT | Always passes | Public/private endpoints |
| `@owner_only` | Check ownership | 403 if not owner | User resources |
| `@role_required` | Check role | 403 if no role | Admin endpoints |
| `@permission_required` | Check permission | 403 if missing | Advanced AC |
| `@rate_limit` | Limit requests | 429 if exceeded | Protect expensive ops |
| `@validate_json` | Validate fields | 400 if missing | Input validation |
