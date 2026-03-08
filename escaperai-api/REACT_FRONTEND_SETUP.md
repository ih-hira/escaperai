"""
React Frontend API Integration - Example Configuration
Shows how to set up a React app to work with the EscapeRAI Flask API
"""

# This file contains JavaScript/React code examples for frontend setup


# ============================================================================
# FILE: src/config/api.js
# Description: API configuration
# ============================================================================

"""
// Configure your API endpoint here
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

// API endpoints
export const API_ENDPOINTS = {
  AUTH: {
    REGISTER: '/api/auth/register',
    LOGIN: '/api/auth/login',
    REFRESH: '/api/auth/refresh',
    LOGOUT: '/api/auth/logout',
  },
  TRIPS: {
    LIST: '/api/trips',
    CREATE: '/api/trips',
    GET: (id) => `/api/trips/${id}`,
    UPDATE: (id) => `/api/trips/${id}`,
    DELETE: (id) => `/api/trips/${id}`,
    ADD_ITINERARY: (id) => `/api/trips/${id}/itinerary`,
    GENERATE_ITINERARY: (id) => `/api/trips/${id}/itinerary/generate`,
  }
};

// HTTP Client configuration
export const HTTP_CLIENT_CONFIG = {
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
};

export default API_BASE_URL;
"""


# ============================================================================
# FILE: src/api/client.js
# Description: Axios HTTP client with interceptors
# ============================================================================

"""
import axios from 'axios';
import { API_ENDPOINTS, HTTP_CLIENT_CONFIG } from '../config/api';

// Create axios instance
const apiClient = axios.create(HTTP_CLIENT_CONFIG);

// Request interceptor - Add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - Handle errors
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Handle 401 Unauthorized
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Try to refresh token
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(
          `${HTTP_CLIENT_CONFIG.baseURL}/api/auth/refresh`,
          { refresh_token: refreshToken }
        );

        const newAccessToken = response.data.data.access_token;
        localStorage.setItem('access_token', newAccessToken);

        // Retry original request
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Refresh failed, redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;
"""


# ============================================================================
# FILE: src/api/auth.js
# Description: Authentication API calls
# ============================================================================

"""
import apiClient from './client';
import { API_ENDPOINTS } from '../config/api';

export const authAPI = {
  register: async (email, password) => {
    const response = await apiClient.post(API_ENDPOINTS.AUTH.REGISTER, {
      email,
      password
    });
    return response.data;
  },

  login: async (email, password) => {
    const response = await apiClient.post(API_ENDPOINTS.AUTH.LOGIN, {
      email,
      password
    });
    return response.data;
  },

  refresh: async (refreshToken) => {
    const response = await apiClient.post(API_ENDPOINTS.AUTH.REFRESH, {
      refresh_token: refreshToken
    });
    return response.data;
  },

  logout: async () => {
    try {
      await apiClient.post(API_ENDPOINTS.AUTH.LOGOUT);
    } catch (error) {
      console.error('Logout error:', error);
    }
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }
};

export default authAPI;
"""


# ============================================================================
# FILE: src/api/trips.js
# Description: Trips API calls
# ============================================================================

"""
import apiClient from './client';
import { API_ENDPOINTS } from '../config/api';

export const tripsAPI = {
  // List all trips
  list: async () => {
    const response = await apiClient.get(API_ENDPOINTS.TRIPS.LIST);
    return response.data;
  },

  // Create new trip
  create: async (tripData) => {
    const response = await apiClient.post(API_ENDPOINTS.TRIPS.CREATE, tripData);
    return response.data;
  },

  // Get single trip
  get: async (id) => {
    const response = await apiClient.get(API_ENDPOINTS.TRIPS.GET(id));
    return response.data;
  },

  // Update trip
  update: async (id, tripData) => {
    const response = await apiClient.put(
      API_ENDPOINTS.TRIPS.UPDATE(id),
      tripData
    );
    return response.data;
  },

  // Delete trip
  delete: async (id) => {
    const response = await apiClient.delete(API_ENDPOINTS.TRIPS.DELETE(id));
    return response.data;
  },

  // Add itinerary item
  addItinerary: async (id, itineraryData) => {
    const response = await apiClient.post(
      API_ENDPOINTS.TRIPS.ADD_ITINERARY(id),
      itineraryData
    );
    return response.data;
  },

  // Generate itinerary template
  generateItinerary: async (id, templateType = 'standard') => {
    const response = await apiClient.post(
      API_ENDPOINTS.TRIPS.GENERATE_ITINERARY(id),
      { template_type: templateType }
    );
    return response.data;
  }
};

export default tripsAPI;
"""


# ============================================================================
# FILE: src/hooks/useTrips.js
# Description: Custom hook for trip management
# ============================================================================

"""
import { useState, useCallback } from 'react';
import tripsAPI from '../api/trips';

export const useTrips = () => {
  const [trips, setTrips] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const listTrips = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await tripsAPI.list();
      setTrips(data.data);
      return data;
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load trips');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const createTrip = useCallback(async (tripData) => {
    setLoading(true);
    setError(null);
    try {
      const data = await tripsAPI.create(tripData);
      setTrips([...trips, data.data]);
      return data;
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to create trip');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [trips]);

  const updateTrip = useCallback(async (id, tripData) => {
    setLoading(true);
    setError(null);
    try {
      const data = await tripsAPI.update(id, tripData);
      setTrips(trips.map(t => t.id === id ? data.data : t));
      return data;
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to update trip');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [trips]);

  const deleteTrip = useCallback(async (id) => {
    setLoading(true);
    setError(null);
    try {
      const data = await tripsAPI.delete(id);
      setTrips(trips.filter(t => t.id !== id));
      return data;
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to delete trip');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [trips]);

  const generateItinerary = useCallback(async (id, templateType) => {
    setLoading(true);
    setError(null);
    try {
      const data = await tripsAPI.generateItinerary(id, templateType);
      setTrips(trips.map(t => t.id === id ? data.data : t));
      return data;
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to generate itinerary');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [trips]);

  return {
    trips,
    loading,
    error,
    listTrips,
    createTrip,
    updateTrip,
    deleteTrip,
    generateItinerary
  };
};
"""


# ============================================================================
# FILE: .env.example
# Description: React environment variables
# ============================================================================

"""
# Backend API URL
REACT_APP_API_URL=http://localhost:5000

# App settings
REACT_APP_NAME=EscapeRAI
REACT_APP_VERSION=1.0.0
"""


# ============================================================================
# FILE: package.json (dependencies to install)
# ============================================================================

"""
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.4.0",
    "react-router-dom": "^6.0.0",
    "zustand": "^4.0.0"
  },
  "devDependencies": {
    "vite": "^4.0.0",
    "@vitejs/plugin-react": "^3.0.0"
  }
}
"""


# ============================================================================
# EXAMPLE: React Component using the API
# ============================================================================

"""
// File: src/pages/TripsPage.jsx
import { useEffect, useState } from 'react';
import { useTrips } from '../hooks/useTrips';
import tripAPI from '../api/trips';

export const TripsPage = () => {
  const { trips, loading, error, listTrips, createTrip, generateItinerary } = useTrips();
  const [newTrip, setNewTrip] = useState({
    destination: '',
    start_date: '',
    end_date: ''
  });

  useEffect(() => {
    listTrips();
  }, [listTrips]);

  const handleCreateTrip = async (e) => {
    e.preventDefault();
    try {
      await createTrip(newTrip);
      setNewTrip({ destination: '', start_date: '', end_date: '' });
    } catch (err) {
      console.error('Error creating trip:', err);
    }
  };

  const handleGenerateItinerary = async (tripId) => {
    try {
      await generateItinerary(tripId, 'standard');
    } catch (err) {
      console.error('Error generating itinerary:', err);
    }
  };

  return (
    <div>
      <h1>My Trips</h1>

      <form onSubmit={handleCreateTrip}>
        <input
          type="text"
          placeholder="Destination"
          value={newTrip.destination}
          onChange={(e) => setNewTrip({ ...newTrip, destination: e.target.value })}
          required
        />
        <input
          type="date"
          value={newTrip.start_date}
          onChange={(e) => setNewTrip({ ...newTrip, start_date: e.target.value })}
          required
        />
        <input
          type="date"
          value={newTrip.end_date}
          onChange={(e) => setNewTrip({ ...newTrip, end_date: e.target.value })}
          required
        />
        <button type="submit" disabled={loading}>Create Trip</button>
      </form>

      {error && <p style={{ color: 'red' }}>{error}</p>}
      {loading && <p>Loading...</p>}

      <ul>
        {trips.map((trip) => (
          <li key={trip.id}>
            <h3>{trip.destination}</h3>
            <p>{trip.start_date} to {trip.end_date}</p>
            <button onClick={() => handleGenerateItinerary(trip.id)}>
              Generate Itinerary
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
};
"""

# ============================================================================
# SETUP INSTRUCTIONS
# ============================================================================

"""
1. Create React app:
   npx create-react-app escaperai-frontend
   cd escaperai-frontend

2. Install dependencies:
   npm install axios react-router-dom zustand

3. Create folder structure:
   src/
   ├── api/
   │   ├── client.js
   │   ├── auth.js
   │   └── trips.js
   ├── config/
   │   └── api.js
   ├── hooks/
   │   ├── useAuth.js
   │   └── useTrips.js
   ├── pages/
   │   ├── LoginPage.jsx
   │   ├── TripsPage.jsx
   │   └── TripDetailPage.jsx
   ├── App.jsx
   └── index.jsx

4. Create .env file:
   REACT_APP_API_URL=http://localhost:5000

5. Copy code from this file into corresponding locations

6. Test with:
   npm start
   (Frontend on http://localhost:3000)

7. Backend should be running on http://localhost:5000
   with CORS_ORIGINS=http://localhost:3000
"""
