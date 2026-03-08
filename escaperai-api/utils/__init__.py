"""Utility modules for the EscapeRAI API."""

from .security import (
    hash_password,
    verify_password,
    validate_password_strength,
    is_password_compromised,
    validate_email,
    is_disposable_email,
    normalize_email,
)

from .jwt_handler import (
    generate_tokens,
    generate_access_token,
    generate_refresh_token,
    verify_token,
    get_user_from_token,
    get_token_claims,
    get_token_expiration,
    is_token_expired,
    get_token_remaining_time,
    create_token_response,
)

from .middleware import (
    auth_required,
    auth_optional,
    owner_only,
    rate_limit,
    validate_json,
    protect,
)

from .itinerary_utils import (
    generate_default_itinerary,
    get_date_range,
    add_activity_to_itinerary,
    remove_activity_from_itinerary,
    get_trip_duration,
    get_activities_count,
    validate_itinerary_structure,
)

__all__ = [
    # Security - Password
    'hash_password',
    'verify_password',
    'validate_password_strength',
    'is_password_compromised',
    # Security - Email
    'validate_email',
    'is_disposable_email',
    'normalize_email',
    # JWT
    'generate_tokens',
    'generate_access_token',
    'generate_refresh_token',
    'verify_token',
    'get_user_from_token',
    'get_token_claims',
    'get_token_expiration',
    'is_token_expired',
    'get_token_remaining_time',
    'create_token_response',
    # Middleware
    'auth_required',
    'auth_optional',
    'owner_only',
    'rate_limit',
    'validate_json',
    'protect',
    # Itinerary
    'generate_default_itinerary',
    'get_date_range',
    'add_activity_to_itinerary',
    'remove_activity_from_itinerary',
    'get_trip_duration',
    'get_activities_count',
    'validate_itinerary_structure',
]
