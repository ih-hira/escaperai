# CORS Configuration Guide for React Frontend

## Overview

CORS (Cross-Origin Resource Sharing) allows your React frontend to make requests to the Flask backend API. This guide covers setting up CORS for development, staging, and production environments.

---

## ✅ Current CORS Configuration

The Flask app is now configured with:
- **Origins**: Configurable via environment variable
- **Methods**: GET, POST, PUT, DELETE, OPTIONS
- **Headers**: Content-Type, Authorization
- **Credentials**: Enabled (for cookies/auth tokens)
- **Max Age**: 3600 seconds (1 hour)

---

## 🚀 Quick Setup

### Step 1: Set Environment Variables

**Development (`.env` or `.env.development`):**
```env
CORS_ORIGINS=http://localhost:3000
```

**Multiple Environments:**
```env
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,https://app.example.com
```

**Production:**
```env
CORS_ORIGINS=https://app.example.com
```

### Step 2: Start Flask Server
```bash
flask run
```

### Step 3: Start React App
```bash
npm start
# or
yarn start
```

---

## 📋 Configuration by Environment

### Development (Local)

**`.env.development`:**
```env
FLASK_ENV=development
CORS_ORIGINS=http://localhost:3000
JWT_SECRET_KEY=dev-secret-key
DATABASE_URL=sqlite:///escaperai.db
```

This allows your React app running on `http://localhost:3000` to access the Flask API.

### Staging

**`.env.staging`:**
```env
FLASK_ENV=staging
CORS_ORIGINS=http://staging.example.com,http://localhost:3000
JWT_SECRET_KEY=your-staging-secret
DATABASE_URL=postgresql://user:pass@staging-db:5432/escaperai
```

### Production

**`.env.production`:**
```env
FLASK_ENV=production
CORS_ORIGINS=https://app.example.com
JWT_SECRET_KEY=your-production-secret
DATABASE_URL=postgresql://user:pass@prod-db:5432/escaperai
```

---

## 🔧 Advanced Configuration

### Custom CORS Configuration

You can further customize CORS in `config.py`:

```python
class DevelopmentConfig(Config):
    """Development configuration"""
    CORS_ORIGINS = ['http://localhost:3000', 'http://localhost:5173']
    CORS_ALLOW_HEADERS = ['Content-Type', 'Authorization', 'X-Custom-Header']
    CORS_EXPOSE_HEADERS = ['Content-Type', 'Authorization', 'X-Total-Count']
    CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS']
    CORS_SUPPORTS_CREDENTIALS = True
    CORS_MAX_AGE = 3600
```

### Allow Wildcard (Not Recommended for Production)

For development only:
```env
CORS_ORIGINS=*
```

⚠️ **WARNING**: Never use `*` in production. It's a security risk.

---

## 🎯 React Frontend Setup

### Install Axios (if using HTTP client)

```bash
npm install axios
```

### Configure API Base URL

**`src/api/config.js`:**
```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

export const api = {
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
};
```

### Create API Service

**`src/api/service.js`:**
```javascript
import axios from 'axios';
import { api } from './config';

const apiClient = axios.create({
  baseURL: api.baseURL,
  timeout: api.timeout,
  headers: api.headers,
  withCredentials: true // Important for CORS with credentials
});

// Add token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle response errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle token expiration
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

### Use in React Components

**`src/hooks/useAuth.js`:**
```javascript
import { useState } from 'react';
import apiClient from '../api/service';

export const useAuth = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const register = async (email, password) => {
    setLoading(true);
    try {
      const response = await apiClient.post('/api/auth/register', {
        email,
        password
      });
      localStorage.setItem('access_token', response.data.data.access_token);
      return response.data;
    } catch (err) {
      setError(err.response?.data?.error || 'Registration failed');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    setLoading(true);
    try {
      const response = await apiClient.post('/api/auth/login', {
        email,
        password
      });
      localStorage.setItem('access_token', response.data.data.access_token);
      return response.data;
    } catch (err) {
      setError(err.response?.data?.error || 'Login failed');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { register, login, loading, error };
};
```

---

## 🧪 Testing CORS

### Test with curl

```bash
# Test preflight request
curl -i -X OPTIONS http://localhost:5000/api/trips \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: GET"

# Should return 200 with CORS headers
```

### Expected Response Headers

```
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
Access-Control-Allow-Credentials: true
Access-Control-Max-Age: 3600
```

### Test with Fetch API

```javascript
// In browser console
fetch('http://localhost:5000/api/trips', {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN',
    'Content-Type': 'application/json'
  },
  credentials: 'include'
})
.then(r => r.json())
.then(d => console.log(d));
```

---

## 🐛 Troubleshooting

### Error: CORS policy: No 'Access-Control-Allow-Origin' header

**Cause**: Origin not in CORS_ORIGINS

**Solution**:
```bash
# Check your frontend URL
echo $CORS_ORIGINS

# Update .env file
CORS_ORIGINS=http://localhost:3000
```

### Error: Credentials mode is 'include' but Access-Control-Allow-Credentials is missing

**Cause**: Missing credentials configuration

**Solution**: Ensure in config:
```python
CORS_SUPPORTS_CREDENTIALS = True
```

And in React:
```javascript
fetch(url, {
  credentials: 'include'  // Important!
})
```

### Error: Method not allowed

**Cause**: HTTP method not in CORS_METHODS

**Solution**: Add method to config:
```python
CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS']
```

### Error: Request header not allowed

**Cause**: Header not in CORS_ALLOW_HEADERS

**Solution**: Add header to config:
```python
CORS_ALLOW_HEADERS = ['Content-Type', 'Authorization', 'X-Custom-Header']
```

---

## 📊 Common CORS Scenarios

### Scenario 1: Local Development

```env
# Server: localhost:5000
# React app: localhost:3000
CORS_ORIGINS=http://localhost:3000
FLASK_ENV=development
```

### Scenario 2: Multiple Dev Tools

```env
# React (port 3000)
# Vite (port 5173)
# Svelte (port 5000)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:5000
```

### Scenario 3: Development + Production

```env
# Dev and prod both need access
CORS_ORIGINS=http://localhost:3000,https://app.example.com
```

### Scenario 4: Subdomain Support

```env
# Allow all subdomains in production
CORS_ORIGINS=https://app.example.com,https://www.example.com,https://api.example.com
```

---

## 🔒 Security Best Practices

### ✅ DO:
- Specify exact origins (not wildcard)
- Use HTTPS in production
- Validate origins server-side
- Limit HTTP methods
- Whitelist specific headers
- Use credentials only when needed

### ❌ DON'T:
- Use `CORS_ORIGINS=*` in production
- Include sensitive data in CORS headers
- Allow all methods without restriction
- Skip authentication for CORS requests
- Ignore preflight failures

---

## 📝 Environment Setup Examples

### Create `.env.development`

```bash
cp .sample.env .env.development
```

Then edit:

```env
SECRET_KEY=dev-secret-key
JWT_SECRET_KEY=dev-jwt-secret
DATABASE_URL=sqlite:///escaperai_dev.db
FLASK_ENV=development
CORS_ORIGINS=http://localhost:3000
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=2592000
```

### Create `.env.production`

```bash
cp .sample.env .env.production
```

Then edit:

```env
SECRET_KEY=your-production-secret-key
JWT_SECRET_KEY=your-production-jwt-secret
DATABASE_URL=postgresql://user:password@prod-db.example.com/escaperai
FLASK_ENV=production
CORS_ORIGINS=https://app.example.com
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=2592000
```

---

## 🚀 Deploying with CORS

### Heroku/Railway

```bash
# Set environment variables
heroku config:set CORS_ORIGINS=https://your-react-app.vercel.app
heroku config:set JWT_SECRET_KEY=your-production-secret
heroku config:set DATABASE_URL=postgresql://...
```

### Docker

**`docker-compose.yml`:**
```yaml
version: '3.8'
services:
  flask:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - CORS_ORIGINS=https://app.example.com
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - DATABASE_URL=${DATABASE_URL}
  
  react:
    build: ../escaperai-frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:5000
```

---

## 📚 Related Documentation

- [JWT_SETUP.md](JWT_SETUP.md) - Authentication tokens
- [MIDDLEWARE_QUICK_REFERENCE.md](MIDDLEWARE_QUICK_REFERENCE.md) - Middleware setup
- [AUTH_401_TROUBLESHOOTING.md](AUTH_401_TROUBLESHOOTING.md) - Auth issues

---

## 💡 Quick Reference

| Setting | Default | Purpose |
|---------|---------|---------|
| CORS_ORIGINS | localhost:3000 | Allowed frontend URLs |
| CORS_METHODS | GET, POST, PUT, DELETE, OPTIONS | Allowed HTTP methods |
| CORS_ALLOW_HEADERS | Content-Type, Authorization | Allowed request headers |
| CORS_EXPOSE_HEADERS | Content-Type, Authorization | Headers exposed to frontend |
| CORS_SUPPORTS_CREDENTIALS | true | Allow cookies/auth |
| CORS_MAX_AGE | 3600 | Preflight cache time (seconds) |

---

## ✨ Summary

Your Flask API is now configured with:
- ✅ Flexible CORS configuration via environment variables
- ✅ Support for multiple origins
- ✅ Proper credential handling
- ✅ Production-ready security settings
- ✅ Easy switching between environments

**Next Step**: Set up your React frontend to use the API with the configuration examples above!

