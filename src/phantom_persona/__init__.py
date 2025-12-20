"""Phantom Persona - Browser automation library with anti-detect capabilities.

A powerful Python library for browser automation built on Playwright,
featuring unique fingerprints, behavioral patterns, and multi-level
protection against anti-bot systems.
"""

from phantom_persona.config import (
    BehaviorConfig,
    BrowserConfig,
    ConfigLoader,
    FingerprintConfig,
    PhantomConfig,
    ProtectionLevel,
    ProxyConfig,
    RetryConfig,
    get_level_description,
    get_plugins_for_level,
)
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
)
from phantom_persona.persona import DeviceInfo, Fingerprint, GeoInfo, Persona
from phantom_persona.proxy import ProxyInfo

__version__ = "0.1.0"

__all__ = [
    # Version
    "__version__",
    # Exceptions
    "PhantomException",
    "BrowserException",
    "BrowserLaunchError",
    "BrowserContextError",
    "ProxyException",
    "ProxyValidationError",
    "ProxyConnectionError",
    "PersonaException",
    "PersonaNotFoundError",
    "PersonaExpiredError",
    "ConfigException",
    "ConfigNotFoundError",
    "ConfigValidationError",
    "DetectionException",
    # Configuration
    "PhantomConfig",
    "BrowserConfig",
    "ProxyConfig",
    "FingerprintConfig",
    "BehaviorConfig",
    "RetryConfig",
    "ConfigLoader",
    "ProtectionLevel",
    "get_plugins_for_level",
    "get_level_description",
    # Persona
    "GeoInfo",
    "DeviceInfo",
    "Fingerprint",
    "Persona",
    # Proxy
    "ProxyInfo",
]
