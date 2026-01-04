"""Common utility functions shared across all platforms."""

import re

# Security constants
MAX_HEADERS_LENGTH = 50000  # 50KB max for headers input
MAX_HEADER_VALUE_LENGTH = 10000  # 10KB max per header value


def parse_raw_headers(
    raw: str,
    required_headers: list[str],
    valid_origins: list[str],
) -> dict | None:
    """
    Parse raw HTTP headers (copied from browser DevTools) into a dict.

    Args:
        raw: Raw HTTP headers string.
        required_headers: List of required header names (lowercase).
        valid_origins: List of allowed origin URL patterns.

    Returns:
        Parsed headers dict, or None if invalid.
    """
    # Sanitize: Check size limit
    if len(raw) > MAX_HEADERS_LENGTH:
        return None

    # Sanitize: Remove null bytes and other control characters (except newlines/tabs)
    raw = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", raw)

    headers = {}
    lines = raw.strip().split("\n")

    for line in lines:
        # Skip request line (e.g., "POST /youtubei/v1/browse...")
        if line.startswith(("GET ", "POST ", "PUT ", "DELETE ", "PATCH ")):
            continue
        # Skip HTTP version lines
        if line.strip().startswith("HTTP/"):
            continue

        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()

            # Sanitize: Skip if value is too long
            if len(value) > MAX_HEADER_VALUE_LENGTH:
                continue

            # Sanitize: Remove any remaining control characters from value
            value = re.sub(r"[\x00-\x1f\x7f]", "", value)

            headers[key] = value

    return headers if headers else None


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
