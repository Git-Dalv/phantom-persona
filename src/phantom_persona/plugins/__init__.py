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
from phantom_persona.plugins.registry import PluginRegistry, register_plugin, registry

__all__ = [
    "Plugin",
    "StealthPlugin",
    "FingerprintPlugin",
    "BehaviorPlugin",
    "PluginRegistry",
    "registry",
    "register_plugin",
]
