"""Plugin system for phantom-persona.

This module provides the plugin architecture for extending and customizing
browser automation with stealth techniques, fingerprint modifications,
and behavioral patterns.
"""

from phantom_persona.plugins.base import (
    BehaviorPlugin,
    FingerprintPlugin,
    Plugin,
    StealthPlugin,
)

__all__ = [
    "Plugin",
    "StealthPlugin",
    "FingerprintPlugin",
    "BehaviorPlugin",
]
