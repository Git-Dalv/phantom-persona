"""Configuration module for phantom-persona.

This module provides Pydantic-based configuration models for all aspects
of the library, including browser settings, proxy configuration, fingerprints,
behavior emulation, and retry logic.
"""

from phantom_persona.config.levels import (
    LEVEL_DESCRIPTIONS,
    LEVEL_PLUGINS,
    ProtectionLevel,
    get_level_description,
    get_plugins_for_level,
    get_recommended_level,
    list_all_levels,
)
from phantom_persona.config.loader import ConfigLoader
from phantom_persona.config.schema import (
    BehaviorConfig,
    BrowserConfig,
    FingerprintConfig,
    PhantomConfig,
    ProxyConfig,
    RetryConfig,
)

__all__ = [
    "BrowserConfig",
    "ProxyConfig",
    "FingerprintConfig",
    "BehaviorConfig",
    "RetryConfig",
    "PhantomConfig",
    "ConfigLoader",
    "ProtectionLevel",
    "LEVEL_PLUGINS",
    "LEVEL_DESCRIPTIONS",
    "get_plugins_for_level",
    "get_level_description",
    "list_all_levels",
    "get_recommended_level",
]
