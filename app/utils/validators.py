"""
Input validation utilities.
"""
import re
from typing import Optional


EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
PASSWORD_MIN_LENGTH = 8


def validate_email(email: str) -> bool:
    """Return True if the email address has a valid format."""
    if not email or not isinstance(email, str):
        return False
    return bool(EMAIL_REGEX.match(email.strip()))


def validate_password(password: str) -> bool:
    """
    Password must be:
    - At least 8 characters
    - Contain at least one digit
    - Contain at least one uppercase and one lowercase letter
    """
    if len(password) < PASSWORD_MIN_LENGTH:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    return True


def validate_card_number(number: str) -> bool:
    """Validate a credit card number using the Luhn algorithm."""
    digits = re.sub(r"\D", "", number)
    if len(digits) < 13 or len(digits) > 19:
        return False
    total = 0
    reverse_digits = digits[::-1]
    for i, digit in enumerate(reverse_digits):
        n = int(digit)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0


def validate_zip_code(zip_code: str, country: str = "US") -> bool:
    """Validate ZIP/postal codes for common countries."""
    patterns = {
        "US": r"^\d{5}(-\d{4})?$",
        "UK": r"^[A-Z]{1,2}\d[A-Z\d]? ?\d[A-Z]{2}$",
        "IN": r"^\d{6}$",
    }
    pattern = patterns.get(country.upper())
    if pattern is None:
        return True  # Unknown country: accept anything
    return bool(re.match(pattern, zip_code.strip(), re.IGNORECASE))


def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
    """Strip whitespace and optionally truncate."""
    cleaned = value.strip()
    if max_length and len(cleaned) > max_length:
        cleaned = cleaned[:max_length]
    return cleaned
