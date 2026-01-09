"""Common utility functions shared across all platforms."""

import re


def sanitize_cookie(cookie: str) -> str:
    """
    Sanitize cookie string by removing potentially dangerous patterns.
    """
    # Remove any script tags or event handlers (defense in depth)
    cookie = re.sub(r"<[^>]*>", "", cookie)
    # Remove javascript: protocol
    cookie = re.sub(r"javascript:", "", cookie, flags=re.IGNORECASE)
    return cookie


def is_valid_origin(origin: str, allowed_patterns: list[str]) -> bool:
    """
    Validate that origin matches one of the allowed patterns.
    """
    return any(re.match(pattern, origin) for pattern in allowed_patterns)
