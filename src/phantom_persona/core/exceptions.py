"""Exception hierarchy for phantom-persona library.

This module defines all custom exceptions used throughout the library,
organized in a clear hierarchy for better error handling and debugging.
"""

from typing import Any, Dict, Optional


class PhantomException(Exception):
    """Base exception for all phantom-persona errors.

    All custom exceptions in the library inherit from this base class,
    making it easy to catch all library-specific errors.

    Attributes:
        message: Human-readable error message
        details: Optional dictionary with additional error context
    """

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Initialize exception with message and optional details.

        Args:
            message: Human-readable error message
            details: Optional dictionary with additional error context
        """
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        """Return string representation of the exception."""
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message

    def __repr__(self) -> str:
        """Return detailed representation of the exception."""
        return f"{self.__class__.__name__}(message={self.message!r}, details={self.details!r})"


# Browser-related exceptions
class BrowserException(PhantomException):
    """Base exception for browser-related errors.

    Raised when there are issues with browser operations, including
    launch failures, context creation problems, or navigation errors.
    """


class BrowserLaunchError(BrowserException):
    """Raised when browser fails to launch.

    This can occur due to missing browser binaries, invalid launch options,
    insufficient system resources, or permission issues.

    Example:
        raise BrowserLaunchError(
            "Failed to launch Chromium browser",
            details={"browser": "chromium", "timeout": 30000}
        )
    """


class BrowserContextError(BrowserException):
    """Raised when browser context creation or operation fails.

    Browser contexts are isolated sessions within a browser instance.
    This exception is raised when context creation fails or when operations
    on an existing context encounter errors.

    Example:
        raise BrowserContextError(
            "Failed to create browser context with fingerprint",
            details={"fingerprint_id": "fp_123", "reason": "invalid viewport"}
        )
    """


# Proxy-related exceptions
class ProxyException(PhantomException):
    """Base exception for proxy-related errors.

    Raised when there are issues with proxy configuration, validation,
    or connection establishment.
    """


class ProxyValidationError(ProxyException):
    """Raised when proxy configuration is invalid.

    This exception is raised during proxy configuration validation,
    before attempting to establish a connection.

    Example:
        raise ProxyValidationError(
            "Invalid proxy URL format",
            details={"url": "invalid://proxy", "expected_format": "http://host:port"}
        )
    """


class ProxyConnectionError(ProxyException):
    """Raised when connection to proxy server fails.

    This can occur due to network issues, incorrect credentials,
    proxy server unavailability, or firewall restrictions.

    Example:
        raise ProxyConnectionError(
            "Failed to connect to proxy server",
            details={"server": "proxy.example.com:8080", "timeout": 5000}
        )
    """


# Persona-related exceptions
class PersonaException(PhantomException):
    """Base exception for persona-related errors.

    Personas represent unique browser identities with specific fingerprints
    and behavioral patterns. This exception covers all persona management errors.
    """


class PersonaNotFoundError(PersonaException):
    """Raised when requested persona does not exist.

    This exception is raised when trying to load or access a persona
    that hasn't been created or has been deleted.

    Example:
        raise PersonaNotFoundError(
            "Persona not found in storage",
            details={"persona_id": "persona_abc123", "storage_path": "/data/personas"}
        )
    """


class PersonaExpiredError(PersonaException):
    """Raised when persona has expired and can no longer be used.

    Personas may have expiration dates to ensure fingerprints remain
    realistic and up-to-date. This exception is raised when attempting
    to use an expired persona.

    Example:
        raise PersonaExpiredError(
            "Persona has expired and cannot be used",
            details={"persona_id": "persona_xyz", "expired_at": "2024-01-01T00:00:00Z"}
        )
    """


# Configuration-related exceptions
class ConfigException(PhantomException):
    """Base exception for configuration-related errors.

    Configuration errors occur when loading, parsing, or validating
    configuration files or settings.
    """


class ConfigNotFoundError(ConfigException):
    """Raised when configuration file is not found.

    This exception is raised when attempting to load a configuration
    file that doesn't exist at the specified path.

    Example:
        raise ConfigNotFoundError(
            "Configuration file not found",
            details={"path": "/configs/settings.yaml", "config_type": "main"}
        )
    """


class ConfigValidationError(ConfigException):
    """Raised when configuration validation fails.

    Configuration must conform to expected schema and value constraints.
    This exception is raised when validation fails.

    Example:
        raise ConfigValidationError(
            "Invalid protection level in configuration",
            details={"field": "protection_level", "value": 10, "allowed": [0, 1, 2, 3, 4]}
        )
    """


# Detection-related exceptions
class DetectionException(PhantomException):
    """Raised when anti-bot system detects automation.

    This is a critical exception indicating that the target website's
    anti-bot protection has detected the automation and potentially
    blocked access. When this occurs, you may need to:
    - Increase protection level
    - Use different fingerprints
    - Add more realistic behavioral patterns
    - Change proxy/IP address

    Example:
        raise DetectionException(
            "Automation detected by anti-bot system",
            details={
                "url": "https://example.com",
                "detection_method": "cloudflare_challenge",
                "protection_level": 2,
                "suggestion": "Try protection_level=4"
            }
        )
    """


# Session-related exceptions
class SessionError(PhantomException):
    """Raised when session operation fails.

    This exception is raised when session-level operations fail,
    such as creating pages on a closed session or accessing
    session resources that don't exist.

    Example:
        raise SessionError(
            "Cannot create page on closed session",
            details={"session_id": "session_123", "state": "closed"}
        )
    """


__all__ = [
    # Base exception
    "PhantomException",
    # Browser exceptions
    "BrowserException",
    "BrowserLaunchError",
    "BrowserContextError",
    # Proxy exceptions
    "ProxyException",
    "ProxyValidationError",
    "ProxyConnectionError",
    # Persona exceptions
    "PersonaException",
    "PersonaNotFoundError",
    "PersonaExpiredError",
    # Config exceptions
    "ConfigException",
    "ConfigNotFoundError",
    "ConfigValidationError",
    # Detection exception
    "DetectionException",
    # Session exception
    "SessionError",
]
