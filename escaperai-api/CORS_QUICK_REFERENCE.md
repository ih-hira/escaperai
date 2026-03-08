# CORS Setup - Quick Reference

## ✅ Quick Start (5 minutes)

### 1. Update `.env` file
```bash
# For React on localhost:3000
CORS_ORIGINS=http://localhost:3000
```

### 2. Start Flask Server
```bash
flask run
```

### 3. Start React App
```bash
npm start
```

**Done!** Your React frontend can now make API calls to Flask.

---

## 🔧 Configuration

### Backend (.env)

```env
# Single origin (development)
CORS_ORIGINS=http://localhost:3000

# Multiple origins (dev + staging + prod)
CORS_ORIGINS=http://localhost:3000,https://app.example.com,https://staging.example.com

# Production only
CORS_ORIGINS=https://app.example.com
```

### React (.env)

```env
# Development
REACT_APP_API_URL=http://localhost:5000

# Production
REACT_APP_API_URL=https://api.example.com
```

---

## 📡 Frontend API Setup

### Install Dependencies
```bash
npm install axios
```

### Create API Client (`src/api/client.js`)
```javascript
import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:5000',
  withCredentials: true
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default apiClient;
```

### Use in Components
```javascript
import apiClient from '../api/client';

// Get trips
const response = await apiClient.get('/api/trips');

// Create trip
const response = await apiClient.post('/api/trips', {
  destination: 'Paris',
  start_date: '2024-06-01T00:00:00Z',
  end_date: '2024-06-15T00:00:00Z'
});
```

---

## 🧪 Test CORS

### Browser Console
```javascript
fetch('http://localhost:5000/api/trips', {
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN'
  },
  credentials: 'include'
})
.then(r => r.json())
.then(d => console.log(d))
```

### Expected Response
```
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Credentials: true
```

---

## 🐛 Common Issues

| Issue | Fix |
|-------|-----|
| CORS error | Update `CORS_ORIGINS` in `.env` |
| 401 Unauthorized | Add token: `Authorization: Bearer <token>` |
| Token expires | Use refresh token endpoint |
| Empty response | Check `Content-Type: application/json` header |
| Method not allowed | Ensure method (GET/POST/PUT) is in `CORS_METHODS` |

---

## 🔐 Security

✅ Development:
```env
CORS_ORIGINS=http://localhost:3000
```

✅ Production:
```env
CORS_ORIGINS=https://app.example.com
```

❌ Never use in production:
```env
CORS_ORIGINS=*
```

---

## 📚 What Changed

| File | Change |
|------|--------|
| `config.py` | Added CORS settings |
| `app.py` | Updated CORS initialization |
| `.sample.env` | Added CORS_ORIGINS examples |

---

## 🎯 Next Steps

1. ✅ Update `.env` with React frontend URL
2. ✅ Start Flask server (`flask run`)
3. ✅ Create React API client
4. ✅ Test API calls from React
5. ✅ Deploy when ready

See [CORS_SETUP.md](CORS_SETUP.md) for full documentation.
