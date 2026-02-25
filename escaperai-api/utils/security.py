"""
Password hashing and security utilities for user authentication.
Uses werkzeug.security for password hashing with PBKDF2 algorithm.
"""

import os
import re
from werkzeug.security import generate_password_hash, check_password_hash


def generate_salt(length=16):
    """
    Generate a cryptographic salt for password hashing.
    
    Args:
        length (int): Length of the salt in bytes (default: 16)
        
    Returns:
        str: A base64-encoded random salt
    """
    import secrets
    salt_bytes = secrets.token_bytes(length)
    return secrets.token_hex(length)


def hash_password(password, method='pbkdf2:sha256', salt_length=16):
    """
    Hash a password using PBKDF2 with SHA256.
    
    Automatically generates a random salt and incorporates it into the hash.
    The salt is embedded in the returned hash string, so no separate storage is needed.
    
    Args:
        password (str): The plain text password to hash
        method (str): The hashing method to use (default: 'pbkdf2:sha256')
        salt_length (int): Length of the generated salt in bytes (default: 16)
        
    Returns:
        str: The hashed password with embedded salt
        
    Raises:
        ValueError: If password is empty or None
    """
    if not password or not isinstance(password, str):
        raise ValueError("Password must be a non-empty string")
    
    return generate_password_hash(password, method=method, salt_length=salt_length)


def verify_password(password, password_hash):
    """
    Verify a plain text password against a hashed password.
    
    Args:
        password (str): The plain text password to verify
        password_hash (str): The hashed password to verify against
        
    Returns:
        bool: True if password matches the hash, False otherwise
        
    Raises:
        ValueError: If inputs are empty or invalid types
    """
    if not password or not isinstance(password, str):
        raise ValueError("Password must be a non-empty string")
    
    if not password_hash or not isinstance(password_hash, str):
        raise ValueError("Password hash must be a non-empty string")
    
    return check_password_hash(password_hash, password)


def validate_password_strength(password, min_length=8):
    """
    Validate password strength requirements.
    
    Requirements:
    - Minimum length (default: 8 characters)
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    
    Args:
        password (str): The password to validate
        min_length (int): Minimum password length (default: 8)
        
    Returns:
        dict: {
            'valid': bool,
            'errors': list of validation error messages
        }
    """
    errors = []
    
    if not password:
        return {'valid': False, 'errors': ['Password is required']}
    
    if len(password) < min_length:
        errors.append(f'Password must be at least {min_length} characters long')
    
    if not re.search(r'[A-Z]', password):
        errors.append('Password must contain at least one uppercase letter')
    
    if not re.search(r'[a-z]', password):
        errors.append('Password must contain at least one lowercase letter')
    
    if not re.search(r'\d', password):
        errors.append('Password must contain at least one digit')
    
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password):
        errors.append('Password must contain at least one special character')
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }


def get_password_strength_score(password):
    """
    Calculate a password strength score (0-100).
    
    Scoring criteria:
    - Length (0-20 points): 1 point per character, capped at 20
    - Uppercase letters (0-10 points)
    - Lowercase letters (0-10 points)
    - Digits (0-20 points)
    - Special characters (0-20 points)
    - Variety of character types (0-20 points)
    
    Args:
        password (str): The password to score
        
    Returns:
        int: Strength score from 0-100
    """
    if not password:
        return 0
    
    score = 0
    
    # Length scoring
    score += min(len(password), 20)
    
    # Character type scoring
    if re.search(r'[A-Z]', password):
        score += 10
    if re.search(r'[a-z]', password):
        score += 10
    if re.search(r'\d', password):
        score += 20
    if re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password):
        score += 20
    
    # Variety bonus
    char_types = sum([
        bool(re.search(r'[A-Z]', password)),
        bool(re.search(r'[a-z]', password)),
        bool(re.search(r'\d', password)),
        bool(re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password))
    ])
    score += min(char_types * 5, 20)
    
    return min(score, 100)


def is_password_compromised(password):
    """
    Check if password is in common weak passwords list (basic check).
    
    Note: For production, consider using an external service like HaveIBeenPwned API.
    
    Args:
        password (str): The password to check
        
    Returns:
        bool: True if password is in weak list, False otherwise
    """
    weak_passwords = {
        'password', '123456', 'password123', 'admin', 'letmein',
        '123456789', '12345678', 'qwerty', '1234567', 'dragon',
        'monkey', '1234567890', 'abc123', 'password1', 'admin123'
    }
    
    return password.lower() in weak_passwords


def validate_email(email, strict=True):
    """
    Validate email address format.
    
    Checks:
    - Valid email format (local@domain.tld)
    - Minimum length (3 characters)
    - Maximum length (254 characters per RFC 5321)
    - Valid characters (alphanumeric, dots, hyphens, underscores, plus sign)
    - At least one dot in domain (for strict mode)
    - Domain has valid TLD (for strict mode)
    
    Args:
        email (str): The email address to validate
        strict (bool): If True, enforce stricter validation rules (default: True)
        
    Returns:
        dict: {
            'valid': bool,
            'errors': list of validation error messages
        }
    """
    errors = []
    
    if not email:
        return {'valid': False, 'errors': ['Email is required']}
    
    email = email.strip().lower()
    
    # Length validation
    if len(email) < 3:
        errors.append('Email must be at least 3 characters long')
    
    if len(email) > 254:
        errors.append('Email must not exceed 254 characters')
    
    # Check for @ symbol
    if '@' not in email:
        errors.append('Email must contain @ symbol')
        return {'valid': False, 'errors': errors}
    
    # Split into local and domain parts
    parts = email.rsplit('@', 1)
    if len(parts) != 2:
        errors.append('Email must have exactly one @ symbol')
        return {'valid': False, 'errors': errors}
    
    local, domain = parts
    
    # Validate local part (before @)
    if not local or len(local) > 64:
        errors.append('Local part must be 1-64 characters')
    
    if local.startswith('.') or local.endswith('.'):
        errors.append('Local part cannot start or end with a dot')
    
    if '..' in local:
        errors.append('Local part cannot contain consecutive dots')
    
    # Validate local part characters
    # Allow: alphanumeric, dots, hyphens, underscores, plus sign
    if not re.match(r'^[a-z0-9._+\-]+$', local):
        errors.append('Local part contains invalid characters')
    
    # Validate domain part (after @)
    if not domain or len(domain) > 255:
        errors.append('Domain must be 1-255 characters')
    
    if domain.startswith('-') or domain.endswith('-') or domain.startswith('.') or domain.endswith('.'):
        errors.append('Domain cannot start or end with hyphen or dot')
    
    if '..' in domain:
        errors.append('Domain cannot contain consecutive dots')
    
    # Validate domain characters
    if not re.match(r'^[a-z0-9.\-]+$', domain):
        errors.append('Domain contains invalid characters')
    
    if strict:
        # For strict mode, require common domain format
        
        # Check for at least one dot in domain
        if '.' not in domain:
            errors.append('Domain must contain at least one dot (e.g., example.com)')
        
        # Check for valid TLD (at least 2 characters after last dot)
        domain_parts = domain.split('.')
        if len(domain_parts) < 2:
            errors.append('Domain must have a valid TLD')
        else:
            tld = domain_parts[-1]
            if len(tld) < 2:
                errors.append('TLD must be at least 2 characters')
            if not re.match(r'^[a-z]{2,}$', tld):
                errors.append('TLD must contain only letters')
        
        # Each domain label should be 1-63 characters
        for label in domain_parts:
            if not label or len(label) > 63:
                errors.append('Each domain label must be 1-63 characters')
            if label.startswith('-') or label.endswith('-'):
                errors.append('Domain labels cannot start or end with hyphen')
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }


def is_email_valid(email, strict=True):
    """
    Quick check if email is valid.
    
    Args:
        email (str): The email address to validate
        strict (bool): If True, enforce stricter validation (default: True)
        
    Returns:
        bool: True if email is valid, False otherwise
    """
    result = validate_email(email, strict=strict)
    return result['valid']


def is_disposable_email(email):
    """
    Check if email is from a known disposable/temporary email provider.
    
    Note: This is a basic check with common providers. For production,
    consider using a disposable email API service.
    
    Args:
        email (str): The email address to check
        
    Returns:
        bool: True if email appears to be disposable, False otherwise
    """
    if not email or '@' not in email:
        return False
    
    domain = email.split('@')[1].lower()
    
    # Common disposable email domains
    disposable_domains = {
        'tempmail.com', 'guerrillamail.com', '10minutemail.com',
        'throwaway.email', 'mailinator.com', 'spam4.me',
        'temp-mail.org', 'yopmail.com', '10minemail.com',
        'tempmail66.com', 'mailnesia.com', 'throwawaymail.com',
        'fakeinbox.com', 'moakt.com', 'maildrop.cc'
    }
    
    return domain in disposable_domains


def normalize_email(email):
    """
    Normalize email address (lowercase, trim whitespace).
    
    Args:
        email (str): The email address to normalize
        
    Returns:
        str: Normalized email, or None if invalid
    """
    if not email:
        return None
    
    normalized = email.strip().lower()
    
    # Validate after normalization
    if not is_email_valid(normalized):
        return None
    
    return normalized
