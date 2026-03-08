import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Box, 
  TextField, 
  Button, 
  Typography, 
  Alert,
  InputAdornment,
  IconButton,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Paper
} from '@mui/material';
import { Visibility, VisibilityOff, CheckCircle, Cancel } from '@mui/icons-material';
import { useAuth } from '../../context/AuthContext';
import { Link as RouterLink } from 'react-router-dom';
import { api } from '../../services/api';

const PASSWORD_REQUIREMENTS = {
  minLength: 8,
  hasUppercase: { regex: /[A-Z]/, label: 'At least one uppercase letter' },
  hasLowercase: { regex: /[a-z]/, label: 'At least one lowercase letter' },
  hasNumber: { regex: /\d/, label: 'At least one number' },
  hasSpecialChar: { regex: /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/, label: 'At least one special character' }
};

const SignupForm = () => {
  const navigate = useNavigate();
  const { setIsAuthenticated } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [formErrors, setFormErrors] = useState({
    email: '',
    password: '',
    confirmPassword: ''
  });

  const validateEmail = (email) => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!email) return 'Email is required';
    if (!re.test(email)) return 'Invalid email format';
    return '';
  };

  const validatePassword = (password) => {
    if (!password) return 'Password is required';
    if (password.length < PASSWORD_REQUIREMENTS.minLength) {
      return `Password must be at least ${PASSWORD_REQUIREMENTS.minLength} characters`;
    }
    if (!PASSWORD_REQUIREMENTS.hasUppercase.regex.test(password)) {
      return 'Password must contain at least one uppercase letter';
    }
    if (!PASSWORD_REQUIREMENTS.hasLowercase.regex.test(password)) {
      return 'Password must contain at least one lowercase letter';
    }
    if (!PASSWORD_REQUIREMENTS.hasNumber.regex.test(password)) {
      return 'Password must contain at least one number';
    }
    if (!PASSWORD_REQUIREMENTS.hasSpecialChar.regex.test(password)) {
      return 'Password must contain at least one special character';
    }
    return '';
  };

  const validateConfirmPassword = (confirmPassword, password) => {
    if (!confirmPassword) return 'Please confirm your password';
    if (confirmPassword !== password) return 'Passwords do not match';
    return '';
  };

  const checkPasswordRequirement = (password, key) => {
    if (key === 'minLength') {
      return password.length >= PASSWORD_REQUIREMENTS.minLength;
    }
    return PASSWORD_REQUIREMENTS[key].regex.test(password);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear field-specific error when user starts typing
    if (formErrors[name]) {
      setFormErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate form
    const emailError = validateEmail(formData.email);
    const passwordError = validatePassword(formData.password);
    const confirmPasswordError = validateConfirmPassword(
      formData.confirmPassword, 
      formData.password
    );
    
    if (emailError || passwordError || confirmPasswordError) {
      setFormErrors({
        email: emailError,
        password: passwordError,
        confirmPassword: confirmPasswordError
      });
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const userData = {
        email: formData.email,
        password: formData.password
      };

      const response = await api.auth.register(userData);
      console.log('Signup response:', response); // Debug log
      
      // Redirect after successful registration
      navigate('/login', { 
        replace: true,
        state: { 
          message: 'Registration successful! Please log in.',
          email: formData.email
        }
      });
      
    } catch (err) {
      console.error('Signup error:', err); // Debug log
      
      // Handle detailed error responses from backend
      let errorMessage = err.message || 'Registration failed. Please try again.';
      
      // Check if error response contains detailed validation errors
      if (err.response?.data?.details) {
        const details = err.response.data.details;
        if (Array.isArray(details)) {
          errorMessage = details.join('. ');
        }
      }
      
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  return (
    <Box
      component="form"
      onSubmit={handleSubmit}
      sx={{
        width: '100%',
        display: 'flex',
        flexDirection: 'column',
        gap: 2
      }}
    >
      <Typography variant="h5" component="h1" gutterBottom textAlign="center">
        Create Account
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <TextField
        fullWidth
        label="Email"
        name="email"
        type="email"
        value={formData.email}
        onChange={handleChange}
        error={!!formErrors.email}
        helperText={formErrors.email}
        disabled={isLoading}
        required
      />

      <TextField
        fullWidth
        label="Password"
        name="password"
        type={showPassword ? 'text' : 'password'}
        value={formData.password}
        onChange={handleChange}
        error={!!formErrors.password}
        helperText={formErrors.password}
        disabled={isLoading}
        required
        InputProps={{
          endAdornment: (
            <InputAdornment position="end">
              <IconButton
                aria-label="toggle password visibility"
                onClick={togglePasswordVisibility}
                edge="end"
              >
                {showPassword ? <VisibilityOff /> : <Visibility />}
              </IconButton>
            </InputAdornment>
          ),
        }}
      />

      {/* Password Requirements Checklist */}
      <Paper 
        elevation={0} 
        sx={{ 
          p: 2, 
          bgcolor: 'action.hover',
          border: '1px solid',
          borderColor: 'divider'
        }}
      >
        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
          Password must contain:
        </Typography>
        <List sx={{ py: 0 }}>
          <ListItem sx={{ py: 0.5, px: 1 }}>
            <ListItemIcon sx={{ minWidth: 32 }}>
              {formData.password.length >= PASSWORD_REQUIREMENTS.minLength ? (
                <CheckCircle sx={{ fontSize: 20, color: 'success.main' }} />
              ) : (
                <Cancel sx={{ fontSize: 20, color: 'action.disabled' }} />
              )}
            </ListItemIcon>
            <ListItemText 
              primary={`At least ${PASSWORD_REQUIREMENTS.minLength} characters`}
              primaryTypographyProps={{ variant: 'body2' }}
            />
          </ListItem>
          {Object.entries(PASSWORD_REQUIREMENTS).map(([key, value]) => {
            if (key === 'minLength') return null;
            const isMet = checkPasswordRequirement(formData.password, key);
            return (
              <ListItem key={key} sx={{ py: 0.5, px: 1 }}>
                <ListItemIcon sx={{ minWidth: 32 }}>
                  {isMet ? (
                    <CheckCircle sx={{ fontSize: 20, color: 'success.main' }} />
                  ) : (
                    <Cancel sx={{ fontSize: 20, color: 'action.disabled' }} />
                  )}
                </ListItemIcon>
                <ListItemText 
                  primary={value.label}
                  primaryTypographyProps={{ variant: 'body2' }}
                />
              </ListItem>
            );
          })}
        </List>
      </Paper>

      <TextField
        fullWidth
        label="Confirm Password"
        name="confirmPassword"
        type={showPassword ? 'text' : 'password'}
        value={formData.confirmPassword}
        onChange={handleChange}
        error={!!formErrors.confirmPassword}
        helperText={formErrors.confirmPassword}
        disabled={isLoading}
        required
      />

      <Button
        type="submit"
        variant="contained"
        color="primary"
        size="large"
        disabled={isLoading}
        sx={{ mt: 2 }}
      >
        {isLoading ? 'Creating Account...' : 'Sign Up'}
      </Button>

      <Typography variant="body2" textAlign="center" sx={{ mt: 2 }}>
        Already have an account?{' '}
        <RouterLink to="/login" style={{ textDecoration: 'none' }}>
          Login
        </RouterLink>
      </Typography>
    </Box>
  );
};

export default SignupForm;