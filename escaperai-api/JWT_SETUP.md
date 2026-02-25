# JWT Token Generation and Validation Setup

## Overview

The application now has a complete JWT (JSON Web Token) authentication system implemented using `flask-jwt-extended`. This provides secure token-based authentication for API endpoints.

## Components

### 1. JWT Utilities (`utils/jwt_handler.py`)

Core JWT functions for token generation, validation, and inspection:

#### Token Generation

**`generate_tokens(user_id, additional_claims=None)`**
- Generates both access and refresh tokens for a user
- Returns a dict with access_token, refresh_token, token_type, and expires_in
- Example:
```python
tokens = generate_tokens(user_id=123, additional_claims={'email': 'user@example.com'})
# Returns: {
#     'access_token': '...',
#     'refresh_token': '...',
#     'token_type': 'Bearer',
#     'expires_in': 3600
# }
```

**`generate_access_token(user_id, additional_claims=None, expires_in=None)`**
- Generates only an access token
- Useful for token refresh operations
- Example:
```python
token = generate_access_token(user_id=123, expires_in=7200)
```

**`generate_refresh_token(user_id, additional_claims=None)`**
- Generates a refresh token for use in token refresh endpoints
- Example:
```python
refresh_token = generate_refresh_token(user_id=123)
```

#### Token Verification

**`verify_token(token, refresh=False)`**
- Verifies and decodes a JWT token
- Returns decoded claims if valid
- Raises exception if invalid
- Example:
```python
try:
    claims = verify_token(token)
except Exception as e:
    print(f"Token is invalid: {e}")
```

#### Token Information

**`get_token_expiration(token)`**
- Returns the expiration datetime of a token
- Useful for checking when a token expires
- Example:
```python
exp_time = get_token_expiration(token)
print(f"Token expires at: {exp_time}")
```

**`is_token_expired(token)`**
- Checks if a token has expired
- Returns True if expired or invalid
- Example:
```python
if is_token_expired(token):
    print("Token has expired, please refresh")
```

**`get_token_age(token)`**
- Returns the age of token in seconds
- Example:
```python
age = get_token_age(token)
print(f"Token is {age} seconds old")
```

**`get_token_remaining_time(token)`**
- Returns remaining time in seconds until expiration
- Returns 0 if already expired
- Example:
```python
remaining = get_token_remaining_time(token)
print(f"Token expires in {remaining} seconds")
```

#### Request Context Functions

Use these inside routes protected with `@jwt_required()`:

**`get_user_from_token()`**
- Extracts user ID from current request's JWT token
- Example:
```python
@app.route('/api/protected', methods=['GET'])
@jwt_required()
def protected_route():
    user_id = get_user_from_token()
    return jsonify({'user_id': user_id})
```

**`get_token_claims()`**
- Returns all claims from current request's JWT token
- Example:
```python
@app.route('/api/profile', methods=['GET'])
@jwt_required()
def get_profile():
    claims = get_token_claims()
    email = claims.get('email')
```

#### Utility Functions

**`create_token_response(user_id, additional_claims=None, status_code=200)`**
- Creates a standardized JSON response with tokens
- Example:
```python
response, status = create_token_response(
    user_id=123,
    additional_claims={'email': 'user@example.com'},
    status_code=200
)
return jsonify(response), status
```

**`get_jti_from_token(token)`**
- Extracts JWT ID (jti) claim from token
- Useful for token blacklisting implementation
- Example:
```python
jti = get_jti_from_token(token)
```

### 2. Configuration (`config.py`)

JWT configuration options:

```python
JWT_SECRET_KEY = 'your-secret-key'           # Must be strong and secret
JWT_ACCESS_TOKEN_EXPIRES = 3600              # 1 hour
JWT_REFRESH_TOKEN_EXPIRES = 2592000          # 30 days
JWT_ALGORITHM = 'HS256'                      # HMAC with SHA256
JWT_TOKEN_LOCATION = ['headers']             # Token in Authorization header
JWT_HEADER_NAME = 'Authorization'            # Header name
JWT_HEADER_TYPE = 'Bearer'                   # Token type
```

### 3. Flask-JWT Extension (`app.py`)

JWTManager is initialized in the Flask app with custom error handlers:

- **Expired Token**: Returns 401 with "Token has expired" message
- **Invalid Token**: Returns 401 with "Invalid token" message
- **Missing Token**: Returns 401 with "Authorization required" message

### 4. Authentication Routes (`routes/auth.py`)

Ready-to-use authentication endpoints:

**POST `/api/auth/register`**
- Register a new user
- Validates password strength before storing
- Request: `{"email": "user@example.com", "password": "MyP@ssw0rd123"}`
- Response: User ID and email

**POST `/api/auth/login`**
- Authenticate and receive tokens
- Request: `{"email": "user@example.com", "password": "MyP@ssw0rd123"}`
- Response: Access token, refresh token, and expiration

**POST `/api/auth/refresh`**
- Generate new access token using refresh token
- Header: `Authorization: Bearer <refresh_token>`
- Response: New access token

**GET `/api/auth/verify`**
- Verify current token and get token info
- Header: `Authorization: Bearer <access_token>`
- Response: User ID, email, and token claims

**GET `/api/auth/me`**
- Get current user's profile
- Header: `Authorization: Bearer <access_token>`
- Response: User profile with trips count

**POST `/api/auth/logout`**
- Logout (stub for token revocation)
- Header: `Authorization: Bearer <access_token>`
- Response: Success message

## Environment Variables

Set these in `.env` file:

```
JWT_SECRET_KEY=your-super-secret-key-min-32-chars-recommended
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=2592000
FLASK_ENV=development
```

## Usage Example

### Basic Authentication Flow

```python
from flask import Flask, jsonify
from flask_jwt_extended import jwt_required
from app import app
from utils import generate_tokens, get_user_from_token

# Login endpoint already implemented in routes/auth.py
# It calls generate_tokens(user.id) and returns tokens

# Protected endpoint example
@app.route('/api/trips', methods=['GET'])
@jwt_required()
def get_user_trips():
    user_id = get_user_from_token()
    trips = Trip.query.filter_by(user_id=user_id).all()
    return jsonify([trip.to_dict() for trip in trips])

# Using tokens
if __name__ == '__main__':
    # Login
    response = requests.post('http://localhost:5000/api/auth/login', json={
        'email': 'user@example.com',
        'password': 'MyP@ssw0rd123'
    })
    tokens = response.json()['data']
    access_token = tokens['access_token']
    
    # Use token in request
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get('http://localhost:5000/api/trips', headers=headers)
    trips = response.json()
```

## Token Revocation (TODO)

Currently, token revocation is stubbed in `revoke_token()`. For production, implement:

1. **Option A: Redis Blacklist**
```python
# Store revoked JTI in Redis with expiration
redis_client.setex(f"revoked_token:{jti}", token_expiration, "true")

# Check in a token_in_blacklist_loader
@jwt.token_in_blacklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return redis_client.exists(f"revoked_token:{jti}")
```

2. **Option B: Database Blacklist**
```python
class TokenBlacklist(db.Model):
    jti = db.Column(db.String, primary_key=True)
    expires_at = db.Column(db.DateTime)
    
@jwt.token_in_blacklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return TokenBlacklist.query.filter_by(jti=jti).first() is not None
```

## Security Best Practices

1. **Secret Key**: Use a strong, random secret key (min 32 characters)
   ```python
   import secrets
   secret = secrets.token_urlsafe(32)
   ```

2. **HTTPS Only**: Always use HTTPS in production

3. **Token Expiration**: Keep access token expiration short (1-2 hours)

4. **Refresh Tokens**: Store refresh tokens with longer expiration (7-30 days)

5. **CORS**: Configure CORS properly for your frontend domain

6. **Password Security**: Users should set strong passwords during registration
   - Minimum 8 characters
   - Uppercase, lowercase, digit, and special character

## Testing

```bash
# Register
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"MyP@ssw0rd123"}'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"MyP@ssw0rd123"}'

# Use token
curl -X GET http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer <access_token>"
```

## References

- [Flask-JWT-Extended Documentation](https://flask-jwt-extended.readthedocs.io/)
- [JWT.io](https://jwt.io/) - JWT information and debugging
- [RFC 7519](https://tools.ietf.org/html/rfc7519) - JWT specification
