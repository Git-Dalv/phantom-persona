"""Protection levels and plugin mappings.

This module defines the protection levels available in phantom-persona
and maps each level to the appropriate set of plugins.
"""

from enum import IntEnum
from typing import Dict, List, Union


class ProtectionLevel(IntEnum):
    """Protection levels for browser automation.

    Each level provides increasing sophistication in anti-detection techniques,
    from pure Playwright to maximum stealth with full emulation.

    Attributes:
        NONE: No protection, pure Playwright (level 0)
        BASIC: Basic stealth techniques (level 1)
        MODERATE: Fingerprints and proxy binding (level 2)
        ADVANCED: Full emulation with behavior patterns (level 3)
        STEALTH: Maximum protection with all features (level 4)
    """

    NONE = 0  # Pure Playwright, minimal modifications
    BASIC = 1  # Basic stealth techniques
    MODERATE = 2  # Fingerprints + proxy binding
    ADVANCED = 3  # Full emulation + behavior
    STEALTH = 4  # Maximum protection


# Mapping of protection levels to plugin lists
LEVEL_PLUGINS: Dict[ProtectionLevel, List[str]] = {
    ProtectionLevel.NONE: [
        # No plugins - pure Playwright
    ],
    ProtectionLevel.BASIC: [
        # Basic stealth
        "stealth.basic",  # Hide WebDriver, automation flags
        "fingerprint.navigator",  # Basic navigator fingerprint
    ],
    ProtectionLevel.MODERATE: [
        # All BASIC plugins
        "stealth.basic",
        "stealth.chrome",  # Chrome-specific stealth
        # Fingerprinting
        "fingerprint.navigator",
        "fingerprint.canvas",  # Canvas fingerprint
        "fingerprint.webgl",  # WebGL fingerprint
        "fingerprint.fonts",  # Font fingerprint
        # Basic behavior
        "behavior.delays",  # Human-like delays
    ],
    ProtectionLevel.ADVANCED: [
        # All MODERATE plugins
        "stealth.basic",
        "stealth.chrome",
        "stealth.permissions",  # Permissions API masking
        # Advanced fingerprinting
        "fingerprint.navigator",
        "fingerprint.canvas",
        "fingerprint.webgl",
        "fingerprint.fonts",
        "fingerprint.audio",  # Audio fingerprint
        "fingerprint.screen",  # Screen fingerprint
        # Advanced behavior
        "behavior.delays",
        "behavior.mouse",  # Mouse movements
        "behavior.scroll",  # Scrolling patterns
        "behavior.typing",  # Typing patterns
        # Proxy integration
        "proxy.timezone",  # Timezone matching with proxy
    ],
    ProtectionLevel.STEALTH: [
        # All ADVANCED plugins
        "stealth.basic",
        "stealth.chrome",
        "stealth.permissions",
        "stealth.cdp",  # Chrome DevTools Protocol masking
        "stealth.iframe",  # Iframe stealth
        # Maximum fingerprinting
        "fingerprint.navigator",
        "fingerprint.canvas",
        "fingerprint.webgl",
        "fingerprint.fonts",
        "fingerprint.audio",
        "fingerprint.screen",
        "fingerprint.webrtc",  # WebRTC fingerprint
        "fingerprint.battery",  # Battery API
        # Maximum behavior emulation
        "behavior.delays",
        "behavior.mouse",
        "behavior.scroll",
        "behavior.typing",
        "behavior.interactions",  # Random interactions
        "behavior.patterns",  # Complex behavioral patterns
        # Advanced proxy features
        "proxy.timezone",
        "proxy.geo",  # Geo-location matching
        # Browser quirks
        "quirks.plugins",  # Browser plugins emulation
        "quirks.extensions",  # Extension emulation
    ],
}


# Descriptions for each protection level
LEVEL_DESCRIPTIONS: Dict[ProtectionLevel, str] = {
    ProtectionLevel.NONE: (
        "Level 0 - Minimal Protection:\n"
        "Pure Playwright with minimal modifications. "
        "Suitable for testing and unprotected sites. "
        "No stealth techniques applied."
    ),
    ProtectionLevel.BASIC: (
        "Level 1 - Basic Protection:\n"
        "Basic stealth techniques to hide WebDriver and automation flags. "
        "Basic navigator fingerprint applied. "
        "Suitable for simple sites with basic bot detection."
    ),
    ProtectionLevel.MODERATE: (
        "Level 2 - Standard Protection (Recommended):\n"
        "Comprehensive fingerprinting including Canvas, WebGL, and fonts. "
        "Chrome-specific stealth techniques. "
        "Human-like delays between actions. "
        "Suitable for most protected sites and general web scraping."
    ),
    ProtectionLevel.ADVANCED: (
        "Level 3 - Enhanced Protection:\n"
        "Full fingerprinting with audio and screen characteristics. "
        "Advanced behavior emulation: mouse movements, scrolling, typing. "
        "Permissions API masking and timezone matching. "
        "Suitable for sites with advanced protection like Cloudflare or DataDome."
    ),
    ProtectionLevel.STEALTH: (
        "Level 4 - Maximum Protection:\n"
        "Maximum stealth with all available techniques. "
        "Complete browser quirks emulation including plugins and extensions. "
        "Complex behavioral patterns and random interactions. "
        "WebRTC and Battery API fingerprinting. "
        "Chrome DevTools Protocol masking. "
        "Suitable for maximum protected sites and anti-bot systems."
    ),
}


def get_plugins_for_level(level: Union[ProtectionLevel, int]) -> List[str]:
    """Get list of plugins for a protection level.

    Args:
        level: Protection level (ProtectionLevel enum or int 0-4)

    Returns:
        List of plugin identifiers to activate

    Raises:
        ValueError: If level is invalid

    Example:
        >>> plugins = get_plugins_for_level(ProtectionLevel.MODERATE)
        >>> print(plugins)
        ['stealth.basic', 'stealth.chrome', 'fingerprint.navigator', ...]

        >>> plugins = get_plugins_for_level(2)
        >>> 'fingerprint.canvas' in plugins
        True
    """
    # Convert int to ProtectionLevel if needed
    if isinstance(level, int):
        try:
            level = ProtectionLevel(level)
        except ValueError as e:
            raise ValueError(
                f"Invalid protection level: {level}. Must be 0-4."
            ) from e

    if level not in LEVEL_PLUGINS:
        raise ValueError(f"Unknown protection level: {level}")

    return LEVEL_PLUGINS[level].copy()


def get_level_description(level: Union[ProtectionLevel, int]) -> str:
    """Get description of what a protection level does.

    Args:
        level: Protection level (ProtectionLevel enum or int 0-4)

    Returns:
        Detailed description of the protection level's features

    Raises:
        ValueError: If level is invalid

    Example:
        >>> desc = get_level_description(ProtectionLevel.ADVANCED)
        >>> print(desc)
        Level 3 - Enhanced Protection:
        Full fingerprinting with audio and screen characteristics...

        >>> desc = get_level_description(0)
        >>> 'Minimal Protection' in desc
        True
    """
    # Convert int to ProtectionLevel if needed
    if isinstance(level, int):
        try:
            level = ProtectionLevel(level)
        except ValueError as e:
            raise ValueError(
                f"Invalid protection level: {level}. Must be 0-4."
            ) from e

    if level not in LEVEL_DESCRIPTIONS:
        raise ValueError(f"Unknown protection level: {level}")

    return LEVEL_DESCRIPTIONS[level]


def list_all_levels() -> Dict[int, str]:
    """List all available protection levels with brief descriptions.

    Returns:
        Dictionary mapping level number to description

    Example:
        >>> levels = list_all_levels()
        >>> levels[0]
        'NONE - Pure Playwright, minimal modifications'
        >>> levels[4]
        'STEALTH - Maximum protection with all features'
    """
    return {
        0: "NONE - Pure Playwright, minimal modifications",
        1: "BASIC - Basic stealth techniques",
        2: "MODERATE - Fingerprints + proxy binding (Recommended)",
        3: "ADVANCED - Full emulation + behavior",
        4: "STEALTH - Maximum protection",
    }


def get_recommended_level() -> ProtectionLevel:
    """Get the recommended protection level for general use.

    Returns:
        Recommended protection level (MODERATE/level 2)

    Example:
        >>> recommended = get_recommended_level()
        >>> recommended
        <ProtectionLevel.MODERATE: 2>
    """
    return ProtectionLevel.MODERATE


__all__ = [
    "ProtectionLevel",
    "LEVEL_PLUGINS",
    "LEVEL_DESCRIPTIONS",
    "get_plugins_for_level",
    "get_level_description",
    "list_all_levels",
    "get_recommended_level",
]
