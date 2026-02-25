# Email Validation Documentation

## Overview

The email validation system provides comprehensive RFC 5322-compliant email format checking with additional security features like disposable email detection and email normalization.

## Functions

### 1. validate_email(email, strict=True)

Comprehensive email validation with detailed error reporting.

**Parameters:**
- `email` (str): Email address to validate
- `strict` (bool): If True, enforce strict validation rules (default: True)

**Returns:**
```python
{
    'valid': bool,
    'errors': [list of validation error messages]
}
```

**Validation Rules:**

**Length:**
- Minimum: 3 characters
- Maximum: 254 characters (RFC 5321)

**Local Part (before @):**
- Cannot be empty
- Maximum 64 characters
- Cannot start or end with a dot
- No consecutive dots
- Valid characters: alphanumeric, `.`, `-`, `_`, `+`

**Domain Part (after @):**
- Cannot be empty
- Maximum 255 characters
- Cannot start or end with hyphen or dot
- No consecutive dots
- Valid characters: alphanumeric, `.`, `-`

**Strict Mode Only:**
- Domain must contain at least one dot
- TLD must be at least 2 characters
- TLD must contain only letters
- Each domain label must be 1-63 characters
- Domain labels cannot start or end with hyphen

**Examples:**

```python
from utils import validate_email

# Valid email
result = validate_email('user@example.com', strict=True)
# Returns: {'valid': True, 'errors': []}

# Invalid email with details
result = validate_email('invalid..email@domain.com', strict=True)
# Returns: {
#     'valid': False,
#     'errors': ['Local part cannot contain consecutive dots']
# }

# Non-strict mode allows localhost
result = validate_email('user@localhost', strict=False)
# Returns: {'valid': True, 'errors': []}

# Non-strict mode fails with strict
result = validate_email('user@localhost', strict=True)
# Returns: {
#     'valid': False,
#     'errors': ['Domain must contain at least one dot']
# }
```

### 2. is_email_valid(email, strict=True)

Quick validation check that returns a boolean.

**Parameters:**
- `email` (str): Email address to validate
- `strict` (bool): Use strict validation (default: True)

**Returns:**
- `bool`: True if valid, False otherwise

**Example:**
```python
from utils import is_email_valid

if is_email_valid(user_email, strict=True):
    print("Email is valid")
else:
    print("Email is invalid")
```

### 3. is_disposable_email(email)

Checks if email is from a known disposable/temporary email provider.

**Parameters:**
- `email` (str): Email address to check

**Returns:**
- `bool`: True if disposable, False otherwise

**Supported Disposable Email Domains:**
- tempmail.com
- guerrillamail.com
- 10minutemail.com
- throwaway.email
- mailinator.com
- spam4.me
- temp-mail.org
- yopmail.com
- 10minemail.com
- tempmail66.com
- mailnesia.com
- throwawaymail.com
- fakeinbox.com
- moakt.com
- maildrop.cc

**Example:**
```python
from utils import is_disposable_email

email = 'spam@tempmail.com'
if is_disposable_email(email):
    return "Disposable email addresses are not allowed"
```

**Note:** For production with extensive disposable email checking, consider using:
- [Disposable Email Domain List (DEDL)](https://github.com/ivolo/disposable-email-domains)
- Third-party APIs like [Hunter.io](https://hunter.io/verify) or [ZeroBounce](https://www.zerobounce.net/)

### 4. normalize_email(email)

Normalize email address (lowercase, trim whitespace, and validate).

**Parameters:**
- `email` (str): Email address to normalize

**Returns:**
- `str`: Normalized email if valid, None if invalid

**Example:**
```python
from utils import normalize_email

# All valid variations normalize to same address
emails = [
    'User@Example.COM',
    '  user@example.com  ',
    'USER@EXAMPLE.COM'
]

for email in emails:
    normalized = normalize_email(email)
    print(normalized)  # All print: user@example.com

# Invalid emails return None
invalid = normalize_email('not-an-email')
print(invalid)  # None
```

## Integration with Authentication Routes

### Register Endpoint

The `/api/auth/register` endpoint uses **strict email validation**:

```python
# Validate email format (strict mode)
email_validation = validate_email(email, strict=True)
if not email_validation['valid']:
    return jsonify({
        'success': False,
        'error': 'Invalid email format',
        'details': email_validation['errors']
    }), 400

# Normalize email
email = normalize_email(email)

# Check for disposable email
if is_disposable_email(email):
    return jsonify({
        'success': False,
        'error': 'Disposable email addresses are not allowed'
    }), 400
```

**Request:**
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"MyP@ssw0rd123"}'
```

**Response (Invalid Email):**
```json
{
    "success": false,
    "error": "Invalid email format",
    "details": [
        "Local part cannot contain consecutive dots"
    ]
}
```

### Login Endpoint

The `/api/auth/login` endpoint uses **relaxed email validation** (strict=False):

```python
# Validate email format (non-strict mode)
email_validation = validate_email(email, strict=False)
if not email_validation['valid']:
    return jsonify({
        'success': False,
        'error': 'Invalid email format',
        'details': email_validation['errors']
    }), 400

# Normalize email
email = normalize_email(email)

# Find user (case-insensitive due to normalization)
user = User.query.filter_by(email=email).first()
```

## Email Format Examples

### Valid Emails

```
user@example.com
john.doe@company.co.uk
first_last+tag@subdomain.example.org
user123@test-domain.com
admin@localhost.local         (non-strict mode only)
test@192.168.1.1              (non-strict mode only)
```

### Invalid Emails

```
notanemail                     # No @ symbol
@example.com                   # Missing local part
user@                          # Missing domain
user..name@example.com         # Consecutive dots in local part
.user@example.com              # Starts with dot
user.@example.com              # Ends with dot
user name@example.com          # Space in local part
user@domain                    # No TLD (strict mode only)
user@.example.com              # Domain starts with dot
user@example..com              # Domain has consecutive dots
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaappppppppppp@example.com  # Local part too long (>64 chars)
```

## Best Practices

### 1. Always Normalize User Input

```python
# Raw user input
user_email = request.json.get('email')

# Normalize before storing
normalized_email = normalize_email(user_email)
if not normalized_email:
    return error_response("Invalid email")

# Store normalized email
user.email = normalized_email
```

### 2. Use Strict Validation for Registration

```python
# During registration, require strict format
validation = validate_email(email, strict=True)
if not validation['valid']:
    return error_response(validation['errors'])
```

### 3. Use Loose Validation for Login

```python
# During login, be more lenient to help users
# (e.g., localhost for development)
validation = validate_email(email, strict=False)
if not validation['valid']:
    return error_response(validation['errors'])
```

### 4. Prevent Disposable Emails During Registration

```python
# Only check disposable emails during registration
if is_disposable_email(email):
    return error_response("Disposable emails are not allowed")
```

### 5. Provide Detailed Error Messages

```python
result = validate_email(email)
if not result['valid']:
    message = f"Email validation failed:\n"
    for error in result['errors']:
        message += f"• {error}\n"
    return error_response(message)
```

## Performance Considerations

- All validation functions are O(n) where n is email length
- Typical email validation completes in < 1ms
- No external API calls required (for built-in functions)
- Disposable email check uses in-memory set lookup O(1)

## Security Considerations

1. **Always normalize emails before storage** to prevent duplicate accounts
2. **Reject disposable emails** to prevent account abuse
3. **Use strict validation** for registration to ensure deliverable domains
4. **Consider email verification** with confirmation links (not included in this utility)
5. **Be careful with error messages** - don't reveal whether an email exists in system during login

## Testing

Run the example test file:

```bash
python tests/email_validation_examples.py
```

Output will show:
- Valid email examples passing validation
- Invalid email examples with error details
- Strict vs non-strict mode differences
- Disposable email detection
- Email normalization behavior

## Future Enhancements

1. **Email Verification API Integration**
   - Verify email deliverability with external APIs
   - Check for SMTP server existence

2. **Extended Disposable Email List**
   - Integrate with master list from GitHub
   - Regular updates

3. **Domain Reputation Checking**
   - Check domain age and reputation
   - Flag suspicious domains

4. **Role-based Email Detection**
   - Detect and optionally reject role-based emails (admin@, noreply@)
   - Require personal email for accounts

5. **Regex Pattern Caching**
   - Compile regexes once for performance
   - Pre-warm cache on startup
