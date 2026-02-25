# Postman Setup Guide for EscapeRAI API

## Quick Start

### 1. Import Postman Collection

Copy the JSON below and import it into Postman:
1. Open Postman
2. Click **Import** → **Raw Text** (or **Paste** tab)
3. Paste the collection JSON (see below)
4. This creates all API endpoints and automatically handles tokens

### 2. Set Up Environment Variables

Create a new Postman Environment:
1. Click **Environments** (left sidebar)
2. Click **"+"** or **Create**
3. Name it: `EscapeRAI`
4. Add these variables:

| Variable | Initial Value | Current Value |
|----------|---------------|---------------|
| `base_url` | `http://localhost:5000` | `http://localhost:5000` |
| `access_token` | `` | (auto-filled) |
| `refresh_token` | `` | (auto-filled) |
| `user_email` | `testuser@example.com` | `testuser@example.com` |
| `user_password` | `TestP@ss123` | `TestP@ss123` |

5. Select this environment from the dropdown (top-right)

---

## Postman Collection JSON

Copy and import this collection into Postman:

```json
{
    "info": {
        "name": "EscapeRAI API",
        "description": "Complete API collection with auth and token management",
        "version": "1.0"
    },
    "item": [
        {
            "name": "Auth",
            "item": [
                {
                    "name": "1. Register",
                    "request": {
                        "method": "POST",
                        "url": "{{base_url}}/api/auth/register",
                        "header": [
                            {
                                "key": "Content-Type",
                                "value": "application/json"
                            }
                        ],
                        "body": {
                            "mode": "raw",
                            "raw": "{\n  \"email\": \"{{user_email}}\",\n  \"password\": \"{{user_password}}\"\n}"
                        },
                        "description": "Create new user account"
                    }
                },
                {
                    "name": "2. Login",
                    "event": [
                        {
                            "listen": "test",
                            "script": {
                                "exec": [
                                    "if (pm.response.code === 200) {",
                                    "    const response = pm.response.json();",
                                    "    pm.environment.set('access_token', response.data.access_token);",
                                    "    pm.environment.set('refresh_token', response.data.refresh_token);",
                                    "    console.log('✅ Tokens saved successfully');",
                                    "}"
                                ]
                            }
                        }
                    ],
                    "request": {
                        "method": "POST",
                        "url": "{{base_url}}/api/auth/login",
                        "header": [
                            {
                                "key": "Content-Type",
                                "value": "application/json"
                            }
                        ],
                        "body": {
                            "mode": "raw",
                            "raw": "{\n  \"email\": \"{{user_email}}\",\n  \"password\": \"{{user_password}}\"\n}"
                        },
                        "description": "Login and get tokens (Access & Refresh)"
                    }
                },
                {
                    "name": "3. Refresh Token",
                    "event": [
                        {
                            "listen": "prerequest",
                            "script": {
                                "exec": [
                                    "console.log('Using refresh token:', pm.environment.get('refresh_token').substring(0, 30) + '...');"
                                ]
                            }
                        },
                        {
                            "listen": "test",
                            "script": {
                                "exec": [
                                    "if (pm.response.code === 200) {",
                                    "    const response = pm.response.json();",
                                    "    pm.environment.set('access_token', response.data.access_token);",
                                    "    console.log('✅ New access token saved');",
                                    "}"
                                ]
                            }
                        }
                    ],
                    "request": {
                        "method": "POST",
                        "url": "{{base_url}}/api/auth/refresh",
                        "header": [
                            {
                                "key": "Authorization",
                                "value": "Bearer {{refresh_token}}"
                            }
                        ],
                        "description": "Get new access token using refresh token"
                    }
                },
                {
                    "name": "4. Verify Token",
                    "request": {
                        "method": "GET",
                        "url": "{{base_url}}/api/auth/verify",
                        "header": [
                            {
                                "key": "Authorization",
                                "value": "Bearer {{access_token}}"
                            }
                        ],
                        "description": "Verify current access token"
                    }
                },
                {
                    "name": "5. Get Current User Profile",
                    "request": {
                        "method": "GET",
                        "url": "{{base_url}}/api/auth/me",
                        "header": [
                            {
                                "key": "Authorization",
                                "value": "Bearer {{access_token}}"
                            }
                        ],
                        "description": "Get authenticated user's profile"
                    }
                },
                {
                    "name": "6. Logout",
                    "request": {
                        "method": "POST",
                        "url": "{{base_url}}/api/auth/logout",
                        "header": [
                            {
                                "key": "Authorization",
                                "value": "Bearer {{access_token}}"
                            }
                        ],
                        "description": "Logout current user"
                    }
                }
            ]
        },
        {
            "name": "Trips",
            "item": [
                {
                    "name": "1. Create Trip",
                    "request": {
                        "method": "POST",
                        "url": "{{base_url}}/api/trips",
                        "header": [
                            {
                                "key": "Authorization",
                                "value": "Bearer {{access_token}}"
                            },
                            {
                                "key": "Content-Type",
                                "value": "application/json"
                            }
                        ],
                        "body": {
                            "mode": "raw",
                            "raw": "{\n  \"destination\": \"Paris\",\n  \"start_date\": \"2024-06-01T00:00:00Z\",\n  \"end_date\": \"2024-06-15T00:00:00Z\",\n  \"latitude\": 48.8566,\n  \"longitude\": 2.3522\n}"
                        },
                        "description": "Create a new trip"
                    }
                },
                {
                    "name": "2. List All Trips",
                    "request": {
                        "method": "GET",
                        "url": "{{base_url}}/api/trips",
                        "header": [
                            {
                                "key": "Authorization",
                                "value": "Bearer {{access_token}}"
                            }
                        ],
                        "description": "Get all trips for authenticated user"
                    }
                },
                {
                    "name": "3. Get Specific Trip",
                    "request": {
                        "method": "GET",
                        "url": "{{base_url}}/api/trips/1",
                        "header": [
                            {
                                "key": "Authorization",
                                "value": "Bearer {{access_token}}"
                            }
                        ],
                        "description": "Get trip with ID 1 (change 1 to your trip ID)"
                    }
                },
                {
                    "name": "4. Update Trip",
                    "request": {
                        "method": "PUT",
                        "url": "{{base_url}}/api/trips/1",
                        "header": [
                            {
                                "key": "Authorization",
                                "value": "Bearer {{access_token}}"
                            },
                            {
                                "key": "Content-Type",
                                "value": "application/json"
                            }
                        ],
                        "body": {
                            "mode": "raw",
                            "raw": "{\n  \"destination\": \"Barcelona\",\n  \"latitude\": 41.3851,\n  \"longitude\": 2.1734\n}"
                        },
                        "description": "Update trip details"
                    }
                },
                {
                    "name": "5. Delete Trip",
                    "request": {
                        "method": "DELETE",
                        "url": "{{base_url}}/api/trips/1",
                        "header": [
                            {
                                "key": "Authorization",
                                "value": "Bearer {{access_token}}"
                            }
                        ],
                        "description": "Delete trip"
                    }
                },
                {
                    "name": "6. Add Itinerary Item",
                    "request": {
                        "method": "POST",
                        "url": "{{base_url}}/api/trips/1/itinerary",
                        "header": [
                            {
                                "key": "Authorization",
                                "value": "Bearer {{access_token}}"
                            },
                            {
                                "key": "Content-Type",
                                "value": "application/json"
                            }
                        ],
                        "body": {
                            "mode": "raw",
                            "raw": "{\n  \"date\": \"2024-06-05\",\n  \"title\": \"Eiffel Tower Visit\",\n  \"description\": \"Climb to the top and enjoy views\",\n  \"location\": \"5 Avenue Anatole France, Paris\"\n}"
                        },
                        "description": "Add activity to trip itinerary"
                    }
                }
            ]
        },
        {
            "name": "Health Check",
            "request": {
                "method": "GET",
                "url": "{{base_url}}/health",
                "description": "Check API health and database connection"
            }
        }
    ]
}
```

---

## Step-by-Step Guide in Postman

### Step 1: Select Environment
1. Top-right corner, click environment dropdown
2. Select **EscapeRAI**

### Step 2: Register
1. Go to **Auth** → **1. Register**
2. Click **Send**
3. Should get 201 response with user_id

### Step 3: Login (Get Tokens)
1. Go to **Auth** → **2. Login**
2. Click **Send**
3. **Tokens automatically saved** to environment variables via the "Tests" tab script
4. Check: Top-right → Click eye icon to see `access_token` and `refresh_token`

### Step 4: Test Protected Endpoint
1. Go to **Trips** → **1. Create Trip**
2. Click **Send**
3. Should get 201 with trip data

### Step 5: Refresh Token (When Needed)
1. Go to **Auth** → **3. Refresh Token**
2. Click **Send**
3. New `access_token` automatically saved
4. Use it for future requests

---

## Automatic Token Management

The collection includes **Pre-request Scripts** and **Tests** that:
- ✅ Automatically extract tokens from login response
- ✅ Save tokens to environment variables
- ✅ Use tokens in subsequent requests
- ✅ Update access token when refreshed

**How it works:**
1. After **Login**, the Tests script extracts tokens and saves them
2. All other requests use `{{access_token}}` and `{{refresh_token}}`
3. When access token expires, run **Refresh Token**

---

## Manual Token Setup (If Auto Doesn't Work)

### Option 1: Copy-Paste Tokens
1. Login, get response with tokens
2. Copy `access_token` value
3. Top-right → Click eye icon
4. Find `access_token` → Click edit
5. Paste token value

### Option 2: Set via Tests Script
If auto-save isn't working, manually add to any request's **Tests** tab:

```javascript
const response = pm.response.json();
pm.environment.set('access_token', response.data.access_token);
pm.environment.set('refresh_token', response.data.refresh_token);
```

---

## Postman Request Examples

### Register Request
- **Method:** POST
- **URL:** `{{base_url}}/api/auth/register`
- **Body (raw JSON):**
```json
{
  "email": "testuser@example.com",
  "password": "TestP@ss123"
}
```

### Login Request
- **Method:** POST
- **URL:** `{{base_url}}/api/auth/login`
- **Body (raw JSON):**
```json
{
  "email": "testuser@example.com",
  "password": "TestP@ss123"
}
```
- **Tests Tab:** (Auto-saves tokens)
```javascript
if (pm.response.code === 200) {
    const response = pm.response.json();
    pm.environment.set('access_token', response.data.access_token);
    pm.environment.set('refresh_token', response.data.refresh_token);
}
```

### Create Trip Request
- **Method:** POST
- **URL:** `{{base_url}}/api/trips`
- **Headers:**
  - `Authorization: Bearer {{access_token}}`
  - `Content-Type: application/json`
- **Body (raw JSON):**
```json
{
  "destination": "Paris",
  "start_date": "2024-06-01T00:00:00Z",
  "end_date": "2024-06-15T00:00:00Z",
  "latitude": 48.8566,
  "longitude": 2.3522
}
```

---

## Debugging in Postman

### Check Response Status
- Green = 2xx (Success)
- Yellow = 3xx (Redirect)
- Red = 4xx (Client error) or 5xx (Server error)

### View Headers
- Click **Headers** tab
- See auth header details

### Check Tokens
- Top-right → eye icon → See all environment variables
- Verify tokens are saved

### Enable Console
- **View** → **Show Postman Console** (Bottom)
- See request/response details and any errors

### Common Errors in Postman

| Error | Cause | Fix |
|-------|-------|-----|
| 401 Unauthorized | Missing/wrong token | Verify `{{access_token}}` is set |
| 401 (Refresh) | Using access_token instead | Use `{{refresh_token}}` |
| 404 Not Found | Wrong endpoint | Check URL doesn't have trailing slash |
| 400 Bad Request | Missing fields | Add all required JSON fields |

---

## Postman Tips & Tricks

### 1. Use Ctrl+Shift+E to Quick Switch Environments
Quickly toggle between environments without clicking dropdown

### 2. Save Requests
After creating a request, click **Save**
- It saves to your collection automatically

### 3. Use Pre-request Script to Log Info
Add to Pre-request tab:
```javascript
console.log('Token:', pm.environment.get('access_token').substring(0, 30) + '...');
```
View in Postman Console (Ctrl+Alt+C)

### 4. Create Request Folders
Organize requests into folders:
- **Auth**
- **Trips**
- **Itinerary**

### 5. Set Variables from Response
Add to Tests tab:
```javascript
const response = pm.response.json();
pm.environment.set('trip_id', response.data.id);
```

Then use `{{trip_id}}` in next request

### 6. Conditional Requests
```javascript
if (pm.environment.get('access_token')) {
    console.log('✅ Token exists');
} else {
    console.log('❌ No token - please login first');
}
```

---

## Complete Testing Flow in Postman

1. **Register**: Auth → 1. Register → Send
2. **Login**: Auth → 2. Login → Send (tokens auto-saved)
3. **Verify**: Auth → 4. Verify Token → Send (verify your token)
4. **Get Profile**: Auth → 5. Get Current User Profile → Send
5. **Create Trip**: Trips → 1. Create Trip → Send
6. **List Trips**: Trips → 2. List All Trips → Send
7. **Get Trip**: Trips → 3. Get Specific Trip → Send
8. **Update Trip**: Trips → 4. Update Trip → Send
9. **Add Itinerary**: Trips → 6. Add Itinerary Item → Send
10. **Delete Trip**: Trips → 5. Delete Trip → Send
11. **Logout**: Auth → 6. Logout → Send

---

## Exporting Collections

To share your collection:
1. Click **Collections** (left sidebar)
2. Right-click your collection
3. **Export** → Choose format (JSON recommended)
4. Share the JSON file with team members
5. They can **Import** into their Postman

---

## Postman Environment Variables Reference

| Variable | Used For | Example |
|----------|----------|---------|
| `base_url` | All requests | `http://localhost:5000` |
| `access_token` | API requests | `eyJhbGc...` |
| `refresh_token` | Refresh token | `eyJhbGc...` |
| `user_email` | Register/Login | `testuser@example.com` |
| `user_password` | Register/Login | `TestP@ss123` |
| `trip_id` | Specific trip ops | `1` (auto-saved from response) |

---

## Summary

**In Postman, to call the Trips API:**

1. ✅ Select **EscapeRAI** environment (top-right)
2. ✅ Run **Auth → 2. Login** (saves tokens automatically)
3. ✅ Run any request from **Trips** folder
4. ✅ Tokens are automatically added via `{{access_token}}`

The collection handles all auth headers automatically!
