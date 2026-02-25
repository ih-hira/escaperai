"""
Email validation utility examples and test cases.
Demonstrates all available email validation functions.
"""

from utils import validate_email, is_email_valid, is_disposable_email, normalize_email


def test_email_validation():
    """Test email validation functions."""
    
    # Valid emails
    valid_emails = [
        'user@example.com',
        'john.doe+tag@company.co.uk',
        'first_last@subdomain.example.org',
        'user123@test-domain.com',
    ]
    
    print("=== Valid Emails ===")
    for email in valid_emails:
        result = validate_email(email, strict=True)
        print(f"{email}: {result['valid']}")
    
    # Invalid emails
    invalid_emails = [
        'notanemail',                    # No @ symbol
        '@example.com',                  # Missing local part
        'user@',                         # Missing domain
        'user..name@example.com',        # Consecutive dots
        '.user@example.com',             # Starts with dot
        'user.@example.com',             # Ends with dot
        'user@domain',                   # No TLD (strict mode only)
        'user@.example.com',             # Domain starts with dot
        'user@example..com',             # Domain has consecutive dots
        'user name@example.com',         # Space in local part
        'a' * 65 + '@example.com',       # Local part too long
        'user@' + 'a' * 250 + '.com',    # Domain too long
    ]
    
    print("\n=== Invalid Emails (Strict Mode) ===")
    for email in invalid_emails:
        result = validate_email(email, strict=True)
        if not result['valid']:
            print(f"{email}: Invalid")
            for error in result['errors']:
                print(f"  - {error}")
    
    # Strict vs Non-strict
    print("\n=== Strict vs Non-Strict Mode ===")
    edge_cases = [
        'user@localhost',           # No TLD
        'user@internal.corp',       # No public TLD
        'test@192.168.1.1',         # IP address
    ]
    
    for email in edge_cases:
        strict_result = validate_email(email, strict=True)
        loose_result = validate_email(email, strict=False)
        print(f"\n{email}")
        print(f"  Strict: {strict_result['valid']}")
        print(f"  Loose: {loose_result['valid']}")


def test_quick_validation():
    """Test is_email_valid quick check."""
    
    print("\n=== Quick Email Validity Check ===")
    test_cases = [
        'john@example.com',
        'invalid@@example.com',
        'user@domain.co.uk',
        'x@y.z',
    ]
    
    for email in test_cases:
        is_valid = is_email_valid(email, strict=True)
        print(f"{email}: {'Valid' if is_valid else 'Invalid'}")


def test_disposable_emails():
    """Test disposable email detection."""
    
    print("\n=== Disposable Email Detection ===")
    test_emails = [
        'user@example.com',                    # Legitimate
        'test@tempmail.com',                   # Disposable
        'spam@10minutemail.com',               # Disposable
        'user@guerrillamail.com',              # Disposable
        'hello@outlook.com',                   # Legitimate
        'nospam@mailinator.com',               # Disposable
    ]
    
    for email in test_emails:
        is_disposable = is_disposable_email(email)
        status = "Disposable" if is_disposable else "Legitimate"
        print(f"{email}: {status}")


def test_email_normalization():
    """Test email normalization."""
    
    print("\n=== Email Normalization ===")
    test_cases = [
        'User@Example.COM',                    # Mixed case
        '  user@example.com  ',                # Whitespace
        'ADMIN@DOMAIN.ORG',                    # All caps
        'John.Doe@Company.Co.UK',              # Mixed case with dots
    ]
    
    for email in test_cases:
        normalized = normalize_email(email)
        print(f"'{email}' -> '{normalized}'")
    
    # Invalid email normalization
    print("\n=== Normalization Fails for Invalid Emails ===")
    invalid_emails = [
        'not-an-email',
        'double@@domain.com',
        '@nodomain.com',
    ]
    
    for email in invalid_emails:
        normalized = normalize_email(email)
        status = "Normalized" if normalized else "Failed (Invalid)"
        print(f"'{email}': {status}")


def test_validation_details():
    """Test validation with error details."""
    
    print("\n=== Validation Error Details ===")
    problem_emails = [
        'us..er@example.com',
        'user@domain_with_underscore.com',
        'toolongemailaddressthatshouldberejectedlocalpars@example.com',
        'user@.example.com',
    ]
    
    for email in problem_emails:
        result = validate_email(email, strict=True)
        print(f"\n{email}")
        if result['valid']:
            print("  ✓ Valid")
        else:
            print("  ✗ Invalid:")
            for error in result['errors']:
                print(f"    - {error}")


if __name__ == '__main__':
    print("Email Validation Test Suite\n" + "=" * 50)
    
    test_email_validation()
    test_quick_validation()
    test_disposable_emails()
    test_email_normalization()
    test_validation_details()
    
    print("\n" + "=" * 50)
    print("Test suite completed!")
