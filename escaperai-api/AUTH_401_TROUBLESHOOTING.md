# 401 Error Troubleshooting Guide

## The Problem

You're getting **401 Unauthorized** on protected routes even with a valid access token from login.

---

## Step 1: Verify Token Format in Postman

### Check Authorization Header Format

The header must be **exactly** this format:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Not any of these:**
```
Authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...     # ❌ Missing "Bearer"
Authorization: bearer {{access_token}}                      # ❌ Lowercase "bearer"
Authorization: Bearer{{access_token}}                       # ❌ No space after Bearer
```

### In Postman Auth Tab (WRONG WAY)

Don't use the **Auth** tab → **Bearer Token** because it may not interact properly with scripts.

### In Postman Headers Tab (CORRECT WAY)

**Set manually in Headers:**
1. Go to **Headers** tab
2. Add new header:
   - **Key:** `Authorization`
   - **Value:** `Bearer {{access_token}}`
3. Make sure it's **not disabled** (checkbox is checked)

---

## Step 2: Verify Token is Actually Saved

### Check Environment Variables

After login, verify tokens are saved:

1. Top-right corner → Click **eye icon** 
2. Expand **EscapeRAI** environment
3. Look for `access_token` with a value (not empty)

**If empty:**
- Login may have failed
- Tests script may not be working
- Manually copy-paste token (see below)

### Manually Save Token

If auto-save isn't working:

1. Run **Login** request
2. In response, find the `access_token` value
3. Copy the entire token (long string)
4. Click **eye icon** → Find `access_token`
5. Edit it → Paste the full token

---

## Step 3: Verify Flask Secret Key

The issue might be that Flask's JWT secret key is not set or different between requests.

### Check Flask Configuration

Open your `.env` file:

```bash
# .env file in escaperai-api/
JWT_SECRET_KEY=your-super-secret-key-min-32-chars
JWT_ACCESS_TOKEN_EXPIRES=3600
```

**Common Issue:** 
- Default secret is: `your-secret-key-change-in-production`
- If changed, tokens won't validate

### Set a Proper Secret Key

Update `.env`:

```
JWT_SECRET_KEY=my-super-secret-key-at-least-32-characters-long-12345
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=2592000
FLASK_ENV=development
```

**Then restart Flask:**
```bash
# Kill the server (Ctrl+C)
# Restart it
python app.py
```

---

## Step 4: Debug JWT Validation

### Add Debug Logging

Add this to your `utils/middleware.py` to debug:

```python
@auth_required
def protected_route():
    from flask import request, g
    import logging
    
    logger = logging.getLogger(__name__)
    
    # Debug: Log the incoming request
    auth_header = request.headers.get('Authorization', 'MISSING')
    logger.info(f"Auth Header: {auth_header[:50]}..." if len(auth_header) > 50 else f"Auth Header: {auth_header}")
    logger.info(f"User ID: {g.user_id}")
    logger.info(f"JWT Claims: {g.jwt}")
    
    return jsonify({'success': True, 'user_id': g.user_id})
```

### Check Flask Console Output

When you make a request with auth:

**Good (should see this):**
```
Info: Auth Header: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Info: User ID: 1
Info: JWT Claims: {...}
```

**Bad (means token validation failed):**
```
Authorization header missing or malformed
```

---

## Step 5: Test with curl

Test without Postman to isolate the issue:

### Get Token
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"testuser@example.com","password":"TestP@ss123"}'
```

**Response:**
```json
{
    "success": true,
    "data": {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjE...",
        ...
    }
}
```

### Use Token
```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjE..."

curl -X GET http://localhost:5000/api/trips \
  -H "Authorization: Bearer $TOKEN"
```

**If this works with curl but not Postman:** The issue is in Postman setup.

---

## Step 6: Common Postman Issues

### Issue 1: Space After Bearer

**Your header:**
```
Authorization: Bearer {{access_token}}
```

**Postman might add extra space:**
```
Authorization:  Bearer eyJ...    # ❌ Double space
```

**Fix:** Delete the header and recreate it manually

### Issue 2: Token Contains Special Characters

Some tokens might have special characters that need escaping.

**Check if token value has any of these:**
```
" (quote)
\ (backslash)
/ (forward slash - shouldn't)
```

If yes, make sure it's wrapped in quotes in the header value.

### Issue 3: Using Wrong Token Type

Remember: **Use `access_token`, NOT `refresh_token`**

In environment:
- `{{access_token}}` ✅ For API calls
- `{{refresh_token}}` ❌ Only for `/api/auth/refresh`

### Issue 4: Token Expired

Tokens expire after 1 hour by default.

**If token older than 1 hour:**
1. Run **Refresh Token** request
2. New token auto-saved
3. Retry original request

---

## Step 7: Verify Auth Middleware is Working

### Create Simple Debug Endpoint

Add this to `routes/trips.py` temporarily to test:

```python
@trips_bp.route('/debug-auth', methods=['GET'])
@auth_required
def debug_auth():
    """Debug endpoint to test authentication"""
    from flask import g
    return jsonify({
        'success': True,
        'message': 'Auth working!',
        'user_id': g.user_id,
        'jwt': g.jwt
    }), 200
```

### Test It
1. Get access token from login
2. Make request to `GET /api/trips/debug-auth`
3. If it returns user_id, auth is working

---

## Step 8: Check JWT Secret Key Match

### Verify Secret Key is Consistent

The secret key used to **generate** the token must match the secret key used to **validate** it.

### Check Your config.py

```python
class Config:
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
```

### Make Sure .env Has It

```bash
# .env
JWT_SECRET_KEY=your-super-secret-key-at-least-32-chars
```

### Restart Flask After Changing

```bash
# Kill: Ctrl+C
# Restart:
python app.py
```

---

## Step 9: Test Full Flow

### Do This Step-by-Step in Postman

1. **Open new tab**, set environment to **EscapeRAI**

2. **Register request:**
   ```
   POST http://localhost:5000/api/auth/register
   Body: {
     "email": "debug@example.com",
     "password": "DebugP@ss123"
   }
   ```
   - Send → Should get 201

3. **Login request:**
   ```
   POST http://localhost:5000/api/auth/login
   Body: {
     "email": "debug@example.com",
     "password": "DebugP@ss123"
   }
   ```
   - Send → Should get 200 with tokens
   - **Copy the `access_token` value**
   - Right-click response → "Copy as cURL"

4. **Get Trips request:**
   ```
   GET http://localhost:5000/api/trips
   Header: Authorization: Bearer <paste_token_here>
   ```
   - Send → Should get 200

---

## Step 10: Enable Postman Console Logging

1. **View** → **Show Postman Console** (Ctrl+Alt+C)
2. Make request
3. Console shows detailed request/response info including headers
4. Verify `Authorization` header is present and correct

---

## Quick Checklist

```
☐ Flask running: python app.py
☐ .env file exists with JWT_SECRET_KEY
☐ Environment selected in Postman (EscapeRAI)
☐ Logged in and have access_token
☐ Authorization header format: "Bearer {{access_token}}"
☐ Token not expired (within 1 hour)
☐ No extra spaces in header
☐ Using access_token (not refresh_token)
☐ Header is not disabled (checkbox checked)
☐ No special formatting of token value
```

---

## Most Common Fix

**99% of 401 errors are due to:**

1. ❌ Postman Auth tab → Bearer Token (WRONG)
2. ✅ Postman Headers tab → Key: `Authorization`, Value: `Bearer {{access_token}}` (CORRECT)

Try this first:

1. Delete all **Auth** tab entries
2. Go to **Headers** tab
3. Add: `Authorization: Bearer {{access_token}}`
4. Send request
5. Should work now!

---

## If Still Not Working

### Test with Debug Endpoint

Add this to `app.py`:

```python
@app.route('/api/debug-token', methods=['POST'])
def debug_token():
    """Debug endpoint - no auth required"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    if not token:
        return jsonify({
            'error': 'No token provided',
            'header': request.headers.get('Authorization', 'MISSING')
        }), 400
    
    try:
        from utils import verify_token
        decoded = verify_token(token)
        return jsonify({
            'success': True,
            'decoded': decoded
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'token_first_50_chars': token[:50]
        }), 400
```

Test it:
```bash
curl -X POST http://localhost:5000/api/debug-token \
  -H "Authorization: Bearer <your_token>"
```

This shows exactly what's wrong with your token.

---

## Summary

**To fix 401 errors:**

1. Use **Headers tab** (not Auth tab) in Postman
2. Set `Authorization: Bearer {{access_token}}`
3. Restart Flask after any `.env` changes
4. Verify token is in environment variables
5. Make sure `JWT_SECRET_KEY` is set in `.env`
6. Test with curl to isolate Postman issues
7. Check token hasn't expired

Try these steps and let me know which step fails!
