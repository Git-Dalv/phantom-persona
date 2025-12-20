"""Configuration module for phantom-persona.

This module provides Pydantic-based configuration models for all aspects
of the library, including browser settings, proxy configuration, fingerprints,
behavior emulation, and retry logic.
"""

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
]
