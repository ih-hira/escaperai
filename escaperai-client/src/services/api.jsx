const BASE_URL = 'http://localhost:5000';

const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return {
    'Content-Type': 'application/json',
    'Authorization': token ? `Bearer ${token}` : '',
  };
};

const handleResponse = async (response) => {
  const data = await response.json();
  
  if (!response.ok) {
    // For 401 errors, check if it's a failed login attempt or session expiration
    if (response.status === 401) {
      // If there's an error message like "Invalid email or password", 
      // it's a login failure - let the component handle it
      if (data.error && data.error.includes('Invalid')) {
        const error = new Error(data.error);
        error.response = { data };
        error.status = response.status;
        throw error;
      }
      // Otherwise, it's likely a session expiration - redirect to login
      localStorage.removeItem('token');
      window.location.href = '/login';
      throw new Error('Session expired. Please login again.');
    }

    if (response.status === 404) {
      throw new Error('Trip not found');
    }

    // Create an error with detailed information
    const error = new Error(data.error || data.message || 'Request failed');
    error.response = { data };
    error.status = response.status;
    throw error;
  }

  console.log('API Response:', data); // Debug log
  return data;
};

export const api = {
  get: async (endpoint) => {
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      headers: getAuthHeaders(),
    });
    return handleResponse(response);
  },
  
  post: async (endpoint, data) => {
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  put: async (endpoint, data) => {
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  auth: {
    login: async (credentials) => {
      return api.post('/api/auth/login', credentials);
    },

    register: async (userData) => {
      return api.post('/api/auth/register', userData);
    }
  }
};

export default api;