# Middleware Quick Reference

## Decorators at a Glance

### Basic Protection
```python
from utils import auth_required
from flask import g

@app.route('/api/secure')
@auth_required
def secure_endpoint():
    user_id = g.user_id  # Authenticated user ID
    return jsonify({'user_id': user_id})
```

### Optional Authentication
```python
from utils import auth_optional

@app.route('/api/posts')
@auth_optional
def list_posts():
    if g.user_id:
        # User authenticated - show private posts
        pass
    else:
        # User not authenticated - show public posts
        pass
```

### Ownership Check
```python
from utils import owner_only

@app.route('/api/trips/<int:id>') 
@owner_only('id')
def get_trip(id):
    trip = g.resource  # Auto-loaded by decorator
    return jsonify(trip.to_dict())
```

### Input Validation
```python
from utils import validate_json

@app.route('/api/trips', methods=['POST'])
@auth_required
@validate_json('destination', 'start_date', 'end_date')
def create_trip():
    data = request.get_json()
    # All required fields guaranteed present
```

### Rate Limiting
```python
from utils import rate_limit

@app.route('/api/expensive')
@auth_required
@rate_limit(max_requests=10, window_seconds=60)
def expensive_operation():
    # Max 10 requests per minute
    pass
```

### Role/Permission Based
```python
from utils import role_required, permission_required

@app.route('/api/admin/users')
@role_required('admin')
def admin_dashboard():
    pass

@app.route('/api/posts', methods=['POST'])
@permission_required('write:posts')
def create_post():
    pass
```

## Common Patterns

### Securing User Resources
```python
# Get user's own data
@app.route('/api/profile')
@auth_required
def get_profile():
    user_id = g.user_id
    user = User.query.get(user_id)
    return jsonify(user.to_dict())

# Get/update/delete specific resource
@app.route('/api/trips/<int:id>')
@auth_required  
def get_trip(id):
    trip = Trip.query.get(id)
    if trip.user_id != g.user_id:
        return error('Access denied'), 403
    return jsonify(trip.to_dict())
```

### API with Combined Validation
```python
@app.route('/api/trips', methods=['POST'])
@auth_required
@validate_json('destination', 'start_date', 'end_date')
@rate_limit(max_requests=50, window_seconds=3600)
def create_trip():
    # - Must be authenticated
    # - Must have required fields
    # - Max 50 per hour
    data = request.get_json()
    user_id = g.user_id
    # ... create trip ...
```

### Public/Private Mix
```python
@app.route('/api/trips/<int:id>')
@auth_optional
def get_trip(id):
    trip = Trip.query.get(id)
    if not trip:
        return jsonify({'error': 'Not found'}), 404
    
    if g.user_id and trip.user_id == g.user_id:
        # Return full details for owner
        return jsonify(trip.to_detailed_dict())
    elif trip.public:
        # Return public info for authenticated users
        return jsonify(trip.to_public_dict())
    else:
        return jsonify({'error': 'Access denied'}), 403
```

## Decorator Ordering

When combining decorators, **order matters**:

```python
# Good order - from general to specific
@route('/api/trips', methods=['POST'])
@auth_required           # General - requires auth first
@validate_json('...')    # Specific - validate input second
@rate_limit(...)         # Specific - rate limit last
def create_trip():
    pass

# Why this order?
# 1. @auth_required fails fast if no token (no point validating JSON)
# 2. @validate_json fails fast if bad input (no point rate limiting)
# 3. @rate_limit fails last if too many requests (already validated)
```

## Request Context (g object)

When using `@auth_required` or decorators that require auth:

```python
from flask import g

@app.route('/api/data')
@auth_required
def get_data():
    g.user_id    # int - The user ID from token
    g.jwt        # dict - All JWT claims
    # In g.jwt:
    # - 'sub': user ID
    # - 'exp': expiration timestamp
    # - 'iat': issued at timestamp
    # - 'email': (if included in token)
    # - 'jti': JWT ID for blacklisting
```

## Error Responses (HTTP Status Codes)

| Code | Scenario | Middleware |
|------|----------|-----------|
| 401 | Missing/invalid token | `@auth_required` |
| 403 | User doesn't own resource | `@owner_only` / route logic |
| 403 | User lacks role/permission | `@role_required`, `@permission_required` |
| 404 | Resource not found | `@owner_only` |
| 400 | Missing required fields | `@validate_json` |
| 429 | Rate limit exceeded | `@rate_limit` |

## Testing Protected Routes

```python
# Without token - should fail
response = client.get('/api/trips')
assert response.status_code == 401

# With token - should succeed
response = client.get(
    '/api/trips',
    headers={'Authorization': f'Bearer {token}'}
)
assert response.status_code == 200

# Test ownership - different user
response = client.get(
    f'/api/trips/{other_users_trip_id}',
    headers={'Authorization': f'Bearer {my_token}'}
)
assert response.status_code == 403
```

## Environment Setup

```bash
# .env file
JWT_SECRET_KEY=your-super-secret-key-min-32-chars
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=2592000
```

## Available Middlewares

| Middleware | Purpose | Example |
|-----------|---------|---------|
| `@auth_required` | Require authentication | Login required routes |
| `@auth_optional` | Optional authentication | Public/private routes |
| `@owner_only('id')` | Check resource ownership | User CRUD operations |
| `@role_required('role')` | Check user role | Admin-only endpoints |
| `@permission_required('perm')` | Check permissions | Fine-grained access |
| `@rate_limit(max, window)` | Rate limit endpoint | Prevent abuse |
| `@validate_json('fields')` | Validate JSON fields | Input validation |

## Common Use Cases

### 1. Simple Protected Endpoint
```python
@app.route('/api/profile')
@auth_required
def get_profile():
    return jsonify({'user_id': g.user_id})
```

### 2. CRUD Resource (Create)
```python
@app.route('/api/trips', methods=['POST'])
@auth_required
@validate_json('destination', 'start_date', 'end_date')
def create_trip():
    data = request.get_json()
    # ...
```

### 3. CRUD Resource (Read)
```python
@app.route('/api/trips/<int:id>')
@auth_required
def get_trip(id):
    trip = Trip.query.get(id)
    if trip.user_id != g.user_id:
        return error('Access denied'), 403
    return jsonify(trip.to_dict())
```

### 4. CRUD Resource (Update)
```python
@app.route('/api/trips/<int:id>', methods=['PUT'])
@auth_required
@validate_json('destination')
def update_trip(id):
    trip = Trip.query.get(id)
    if trip.user_id != g.user_id:
        return error('Access denied'), 403
    # ... update ...
```

### 5. CRUD Resource (Delete)
```python
@app.route('/api/trips/<int:id>', methods=['DELETE'])
@auth_required
def delete_trip(id):
    trip = Trip.query.get(id)
    if trip.user_id != g.user_id:
        return error('Access denied'), 403
    db.session.delete(trip)
    db.session.commit()
    return jsonify({'success': True})
```

### 6. Public/Private with Auth
```python
@app.route('/api/profile/<int:user_id>')
@auth_optional
def get_profile(user_id):
    user = User.query.get(user_id)
    if g.user_id == user_id:
        return jsonify(user.to_full_dict())
    return jsonify(user.to_public_dict())
```

### 7. Rate Limited Operation
```python
@app.route('/api/generate', methods=['POST'])
@auth_required
@validate_json('prompt')
@rate_limit(max_requests=5, window_seconds=3600)
def generate(self):
    # Expensive operation - limited to 5/hour
    pass
```

## Tips & Tricks

### Get User from Token Anywhere
```python
from flask import g
from utils import auth_required

@app.route('/api/data')
@auth_required
def get_data():
    user_id = g.user_id
    jwt_claims = g.jwt
```

### Combine Multiple Decorators Efficiently
```python
# Stack related decorators
@app.route('/api/resource/<int:id>', methods=['PUT'])
@auth_required
@validate_json('field1', 'field2')
def update_resource(id):
    # Auth first, then validation
    pass
```

### Check Auth Manually (inside function)
```python
from flask_jwt_extended import get_jwt_identity
from utils import get_user_from_token

# If you need to check auth manually:
try:
    user_id = get_user_from_token()
except:
    user_id = None
```

### Test with VS Code REST Client
```rest
@token = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

GET http://localhost:5000/api/trips
Authorization: Bearer {{token}}

POST http://localhost:5000/api/trips
Authorization: Bearer {{token}}
Content-Type: application/json

{
  "destination": "Paris",
  "start_date": "2024-06-01T00:00:00Z",
  "end_date": "2024-06-15T00:00:00Z"
}
```
