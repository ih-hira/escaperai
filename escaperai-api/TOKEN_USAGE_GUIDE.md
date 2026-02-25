# JWT Token Usage Guide

## The Problem

When you call `/api/auth/refresh` with an **access token**, you get **401 Unauthorized** because the endpoint expects a **refresh token**.

---

## Access Token vs Refresh Token

### Access Token
- **Purpose:** Access protected endpoints (e.g., `/api/trips`)
- **Lifetime:** Short (1 hour by default)
- **Used for:** Making API requests that require authentication
- **Decorator:** `@jwt_required()`

### Refresh Token
- **Purpose:** Get a new access token when it expires
- **Lifetime:** Long (30 days by default)
- **Used for:** Calling `/api/auth/refresh` to get new access token
- **Decorator:** `@jwt_required(refresh=True)`

---

## Which Token to Use Where

| Endpoint | Token Type | Example |
|----------|-----------|---------|
| GET `/api/trips` | Access Token | `Authorization: Bearer <access_token>` |
| POST `/api/trips` | Access Token | `Authorization: Bearer <access_token>` |
| GET `/api/auth/me` | Access Token | `Authorization: Bearer <access_token>` |
| POST `/api/auth/refresh` | **Refresh Token** | `Authorization: Bearer <refresh_token>` |
| POST `/api/auth/logout` | Access Token | `Authorization: Bearer <access_token>` |
| GET `/api/auth/verify` | Access Token | `Authorization: Bearer <access_token>` |

---

## Complete Authentication Flow

### Step 1: Register
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "TestP@ss123"
  }'
```

**Response:**
```json
{
    "success": true,
    "message": "User registered successfully",
    "data": {
        "user_id": 1,
        "email": "user@example.com"
    }
}
```

### Step 2: Login (Get Both Tokens)
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "TestP@ss123"
  }'
```

**Response:**
```json
{
    "success": true,
    "data": {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsImV4cCI6MTcwOTAzNjAwMH0...",
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsImV4cCI6MTcxMTYyODAwMH0...",
        "token_type": "Bearer",
        "expires_in": 3600
    }
}
```

**Save both tokens:**
- `access_token` → Use for API requests
- `refresh_token` → Use to get new access token when it expires

### Step 3: Use Access Token for Protected Endpoints
```bash
# Use access_token here
curl -X GET http://localhost:5000/api/trips \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjE..."
```

### Step 4: When Access Token Expires, Use Refresh Token

After ~1 hour, your access token expires. Instead of logging in again, use the refresh token:

```bash
# Use refresh_token here (NOT access_token)
curl -X POST http://localhost:5000/api/auth/refresh \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsImV4cCI6MTcxMTYyODAwMH0..."
```

**Response:**
```json
{
    "success": true,
    "data": {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsImV4cCI6MTcwOTAzNjEwMH0...",
        "token_type": "Bearer",
        "expires_in": 3600
    }
}
```

Now use the new `access_token` for API requests.

---

## Quick Reference

### Login & Get Tokens
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"TestP@ss123"}'
```

### Use Access Token (Most endpoints)
```bash
curl -X GET http://localhost:5000/api/trips \
  -H "Authorization: Bearer <access_token>"
```

### Use Refresh Token (Only for /api/auth/refresh)
```bash
curl -X POST http://localhost:5000/api/auth/refresh \
  -H "Authorization: Bearer <refresh_token>"
```

### Get New Access Token
```bash
curl -X POST http://localhost:5000/api/auth/refresh \
  -H "Authorization: Bearer <refresh_token>"
```

---

## Common Mistakes

### ❌ Wrong: Using Access Token on Refresh Endpoint
```bash
curl -X POST http://localhost:5000/api/auth/refresh \
  -H "Authorization: Bearer <access_token>"
# Result: 401 Unauthorized
```

### ✅ Correct: Using Refresh Token on Refresh Endpoint
```bash
curl -X POST http://localhost:5000/api/auth/refresh \
  -H "Authorization: Bearer <refresh_token>"
# Result: 200 OK + new access_token
```

### ❌ Wrong: Using Refresh Token on Protected Endpoints
```bash
curl -X GET http://localhost:5000/api/trips \
  -H "Authorization: Bearer <refresh_token>"
# Result: 401 Unauthorized
```

### ✅ Correct: Using Access Token on Protected Endpoints
```bash
curl -X GET http://localhost:5000/api/trips \
  -H "Authorization: Bearer <access_token>"
# Result: 200 OK
```

---

## Token Expiration Times

From config:

| Token | Default Expiration |
|-------|-------------------|
| Access Token | 3600 seconds (1 hour) |
| Refresh Token | 2592000 seconds (30 days) |

You can change these in `.env`:
```
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=2592000
```

---

## How to Know Which Token You Have

JWT tokens are divided into three parts separated by dots:
`header.payload.signature`

The `payload` (middle part) contains the token type. You can decode it:

```bash
# Extract and decode the payload
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsInR5cCI6ImFjY2VzcyIsImV4cCI6MTcwOTAzNjAwMH0.xyz"
echo $TOKEN | cut -d. -f2 | base64 -d
```

**Access Token payload:**
```json
{
  "sub": 1,
  "type": "access",
  "exp": 1709036000
}
```

**Refresh Token payload:**
```json
{
  "sub": 1,
  "type": "refresh",
  "exp": 1711628000
}
```

---

## Authentication Endpoints Summary

### POST `/api/auth/register`
- **Purpose:** Create new user account
- **Auth Required:** ❌ No
- **Request:** `email`, `password`
- **Response:** `user_id`, `email`

### POST `/api/auth/login`
- **Purpose:** Authenticate and get tokens
- **Auth Required:** ❌ No
- **Request:** `email`, `password`
- **Response:** `access_token`, `refresh_token`, `expires_in`
- **Token Used:** None

### POST `/api/auth/refresh`
- **Purpose:** Get new access token
- **Auth Required:** ✅ Yes (Refresh Token)
- **Request:** None
- **Response:** `access_token`, `expires_in`
- **Token Used:** `refresh_token` in Authorization header

### GET `/api/auth/verify`
- **Purpose:** Verify current token
- **Auth Required:** ✅ Yes (Access Token)
- **Request:** None
- **Response:** `user_id`, `email`, `token_claims`
- **Token Used:** `access_token` in Authorization header

### GET `/api/auth/me`
- **Purpose:** Get current user profile
- **Auth Required:** ✅ Yes (Access Token)
- **Request:** None
- **Response:** User profile data
- **Token Used:** `access_token` in Authorization header

### POST `/api/auth/logout`
- **Purpose:** Logout user
- **Auth Required:** ✅ Yes (Access Token)
- **Request:** None
- **Response:** Success message
- **Token Used:** `access_token` in Authorization header

---

## Test Script with Proper Token Usage

Save as `test_auth.sh`:

```bash
#!/bin/bash

echo "========== Authentication Flow Test =========="

# Step 1: Register
echo -e "\n1️⃣  REGISTER"
REGISTER=$(curl -s -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "TestP@ss123"
  }')
echo $REGISTER | jq '.'

# Step 2: Login
echo -e "\n2️⃣  LOGIN (Get Access & Refresh Tokens)"
LOGIN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "TestP@ss123"
  }')
echo $LOGIN | jq '.'

ACCESS_TOKEN=$(echo $LOGIN | jq -r '.data.access_token')
REFRESH_TOKEN=$(echo $LOGIN | jq -r '.data.refresh_token')

echo -e "\n✅ Access Token: ${ACCESS_TOKEN:0:50}..."
echo "✅ Refresh Token: ${REFRESH_TOKEN:0:50}..."

# Step 3: Use access token to verify
echo -e "\n3️⃣  VERIFY (Using Access Token)"
curl -s -X GET http://localhost:5000/api/auth/verify \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq '.'

# Step 4: Get user profile with access token
echo -e "\n4️⃣  GET PROFILE (Using Access Token)"
curl -s -X GET http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq '.'

# Step 5: Refresh token (use refresh_token, NOT access_token)
echo -e "\n5️⃣  REFRESH (Using Refresh Token)"
REFRESH=$(curl -s -X POST http://localhost:5000/api/auth/refresh \
  -H "Authorization: Bearer $REFRESH_TOKEN")
echo $REFRESH | jq '.'

NEW_ACCESS_TOKEN=$(echo $REFRESH | jq -r '.data.access_token')
echo -e "\n✅ New Access Token: ${NEW_ACCESS_TOKEN:0:50}..."

# Step 6: Verify new access token works
echo -e "\n6️⃣  VERIFY WITH NEW TOKEN"
curl -s -X GET http://localhost:5000/api/auth/verify \
  -H "Authorization: Bearer $NEW_ACCESS_TOKEN" | jq '.'

# Step 7: Logout
echo -e "\n7️⃣  LOGOUT (Using Access Token)"
curl -s -X POST http://localhost:5000/api/auth/logout \
  -H "Authorization: Bearer $NEW_ACCESS_TOKEN" | jq '.'

echo -e "\n✅ Test completed!"
```

Run it:
```bash
chmod +x test_auth.sh
./test_auth.sh
```

---

## Fix Your 401 Error

### Your Current Request (Wrong)
```bash
curl -X POST http://localhost:5000/api/auth/refresh \
  -H "Authorization: Bearer <access_token>"
# ❌ 401 Unauthorized
```

### Corrected Request
```bash
curl -X POST http://localhost:5000/api/auth/refresh \
  -H "Authorization: Bearer <refresh_token>"
# ✅ 200 OK
```

**The fix:** Use `refresh_token` instead of `access_token` for the `/api/auth/refresh` endpoint.

---

## Summary Table

| Scenario | Endpoint | Token Type | Lifetime |
|----------|----------|-----------|----------|
| Register | POST `/api/auth/register` | None | - |
| Login | POST `/api/auth/login` | None | - |
| Access API | GET/POST `/api/*` | Access | 1 hour |
| Get New Token | POST `/api/auth/refresh` | Refresh | 30 days |
| Get Profile | GET `/api/auth/me` | Access | 1 hour |
| Logout | POST `/api/auth/logout` | Access | 1 hour |
