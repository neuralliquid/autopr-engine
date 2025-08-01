import html
import re
from typing import Any, Dict

from ..validation_models import ValidationResult, ValidationSeverity


class StringValidator:
    """String validation functionality."""

    def _validate_string(self, key: str, value: str) -> ValidationResult:
        """Validate string input for security threats."""
        result = ValidationResult(is_valid=True)

        # Length validation
        if len(value) > self.max_string_length:
            result.errors.append(
                f"String too long for key '{key}': {len(value)} > {self.max_string_length}"
            )
            result.severity = ValidationSeverity.MEDIUM
            result.is_valid = False
            return result

        # SQL Injection detection
        for pattern in self.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                result.errors.append(f"Potential SQL injection detected in '{key}'")
                result.severity = ValidationSeverity.CRITICAL
                result.is_valid = False
                return result

        # XSS detection
        for pattern in self.XSS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                result.errors.append(f"Potential XSS attack detected in '{key}'")
                result.severity = ValidationSeverity.CRITICAL
                result.is_valid = False
                return result

        # Command injection detection
        for pattern in self.COMMAND_INJECTION_PATTERNS:
            if re.search(pattern, value):
                result.errors.append(f"Potential command injection detected in '{key}'")
                result.severity = ValidationSeverity.CRITICAL
                result.is_valid = False
                return result

        # Sanitize HTML entities
        sanitized_value = html.escape(value)

        # Additional sanitization for specific contexts
        if "email" in key.lower():
            if not self._is_valid_email(sanitized_value):
                result.errors.append(f"Invalid email format in '{key}'")
                result.severity = ValidationSeverity.MEDIUM
                result.is_valid = False
                return result

        if "url" in key.lower():
            if not self._is_valid_url(sanitized_value):
                result.errors.append(f"Invalid URL format in '{key}'")
                result.severity = ValidationSeverity.MEDIUM
                result.is_valid = False
                return result

        # Wrap string value in a dictionary to satisfy type constraints
        result.sanitized_data = {"value": sanitized_value}
        return result

    def _is_safe_key(self, key: str) -> bool:
        """Check if key name is safe."""
        # Allow alphanumeric, underscore, hyphen, and dot
        safe_pattern = r"^[a-zA-Z0-9_\-\.]+$"
        return bool(re.match(safe_pattern, key)) and len(key) <= 100

    def _is_valid_email(self, email: str) -> bool:
        """Validate email format."""
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(email_pattern, email))

    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format."""
        url_pattern = r"^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$"
        return bool(re.match(url_pattern, url))
