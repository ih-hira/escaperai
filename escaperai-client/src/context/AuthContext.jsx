import { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for token in localStorage on initial load
    const storedToken = localStorage.getItem('token');
    const tokenExpiresAt = localStorage.getItem('tokenExpiresAt');
    
    if (storedToken) {
      // Check if token has expired
      if (tokenExpiresAt && new Date().getTime() > parseInt(tokenExpiresAt)) {
        // Token expired, clear it
        logout();
      } else {
        setToken(storedToken);
        setIsAuthenticated(true);
      }
    }
    setLoading(false);
  }, []);

  const login = (authData) => {
    // Handle the backend response structure
    // authData should contain: { access_token, refresh_token, token_type, expires_in }
    const token = authData.access_token || authData.token;
    
    if (!token) {
      throw new Error('No access token provided');
    }

    localStorage.setItem('token', token);
    
    // Optionally store refresh token for token refresh flow
    if (authData.refresh_token) {
      localStorage.setItem('refreshToken', authData.refresh_token);
    }
    
    // Optionally store token expiration time
    if (authData.expires_in) {
      const expiresAt = new Date().getTime() + (authData.expires_in * 1000);
      localStorage.setItem('tokenExpiresAt', expiresAt.toString());
    }

    setToken(token);
    setIsAuthenticated(true);
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('tokenExpiresAt');
    setToken(null);
    setIsAuthenticated(false);
  };

  const value = {
    isAuthenticated,
    token,
    loading,
    login,
    logout
  };

  if (loading) {
    return null; // or a loading spinner
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};