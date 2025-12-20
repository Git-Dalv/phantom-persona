"""Core functionality for phantom-persona library."""

from phantom_persona.core.browser import BrowserManager
from phantom_persona.core.context import ContextBuilder, ContextManager
from phantom_persona.core.exceptions import (
    BrowserContextError,
    BrowserException,
    BrowserLaunchError,
    ConfigException,
    ConfigNotFoundError,
    ConfigValidationError,
    DetectionException,
    PersonaException,
    PersonaExpiredError,
    PersonaNotFoundError,
    PhantomException,
    ProxyConnectionError,
    ProxyException,
    ProxyValidationError,
    SessionError,
)
from phantom_persona.core.session import Session

__all__ = [
    # Browser management
    "BrowserManager",
    "ContextBuilder",
    "ContextManager",
    "Session",
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
