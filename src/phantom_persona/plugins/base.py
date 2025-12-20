"""Base plugin classes for phantom-persona.

This module defines the abstract base classes for all plugins in the system.
Plugins are used to apply stealth techniques, modify fingerprints, and
add human-like behavior to browser sessions.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from playwright.async_api import BrowserContext, Page


class Plugin(ABC):
    """Abstract base class for all plugins.

    Plugins are modular components that apply specific modifications
    to browser contexts and pages. Each plugin has a unique name,
    priority for execution order, and can be browser-specific.

    Attributes:
        name: Unique plugin identifier (e.g., "stealth.basic", "fingerprint.canvas")
        priority: Execution order (lower values execute first, default: 100)

    Example:
        >>> class MyPlugin(Plugin):
        ...     name = "custom.myplugin"
        ...     priority = 50
        ...
        ...     async def apply(self, context):
        ...         # Apply modifications to context
        ...         pass
    """

    name: str
    priority: int = 100

    @abstractmethod
    async def apply(self, context: "BrowserContext") -> None:
        """Apply plugin modifications to browser context.

        This method is called once per browser context and should apply
        all necessary modifications. This is the primary entry point for
        most plugins.

        Args:
            context: Playwright browser context to modify

        Example:
            >>> async def apply(self, context):
            ...     await context.add_init_script(
            ...         "Object.defineProperty(navigator, 'webdriver', {get: () => false})"
            ...     )
        """
        pass

    async def apply_to_page(self, page: "Page") -> None:
        """Optionally apply modifications to each page.

        This method is called for each new page/tab in the browser context.
        Override this if you need per-page modifications.

        Args:
            page: Playwright page instance

        Example:
            >>> async def apply_to_page(self, page):
            ...     await page.add_init_script("console.log('Page loaded')")
        """
        pass

    def is_compatible(self, browser_type: str) -> bool:
        """Check if plugin is compatible with browser type.

        Override this to restrict plugin to specific browser types.
        By default, plugins are compatible with all browsers.

        Args:
            browser_type: Browser type ("chromium", "firefox", or "webkit")

        Returns:
            True if plugin is compatible, False otherwise

        Example:
            >>> def is_compatible(self, browser_type):
            ...     # Only works with Chromium
            ...     return browser_type == "chromium"
        """
        return True

    def __repr__(self) -> str:
        """String representation of the plugin.

        Returns:
            Formatted string with plugin class, name, and priority

        Example:
            >>> plugin = MyPlugin()
            >>> repr(plugin)
            '<MyPlugin name=custom.myplugin priority=50>'
        """
        return f"<{self.__class__.__name__} name={self.name} priority={self.priority}>"

    def __lt__(self, other: "Plugin") -> bool:
        """Compare plugins by priority for sorting.

        Allows plugins to be sorted by priority (lower values first).

        Args:
            other: Another plugin to compare with

        Returns:
            True if this plugin has lower priority (should run first)

        Example:
            >>> plugin1 = MyPlugin()
            >>> plugin1.priority = 50
            >>> plugin2 = MyPlugin()
            >>> plugin2.priority = 100
            >>> plugin1 < plugin2
            True
        """
        return self.priority < other.priority


class StealthPlugin(Plugin):
    """Base class for stealth/anti-detection plugins.

    Stealth plugins are designed to hide automation indicators
    and make the browser appear more human-like to detection systems.

    Examples of stealth plugins:
    - Hiding WebDriver flag
    - Masking Chrome DevTools Protocol
    - Removing automation indicators
    - Spoofing browser properties

    Example:
        >>> class WebDriverStealthPlugin(StealthPlugin):
        ...     name = "stealth.webdriver"
        ...     priority = 10
        ...
        ...     async def apply(self, context):
        ...         await context.add_init_script('''
        ...             Object.defineProperty(navigator, 'webdriver', {
        ...                 get: () => false
        ...             });
        ...         ''')
    """

    pass


class FingerprintPlugin(Plugin):
    """Base class for fingerprint modification plugins.

    Fingerprint plugins modify browser characteristics that can be used
    to identify and track users, creating unique browser identities.

    Examples of fingerprint plugins:
    - Canvas fingerprinting
    - WebGL fingerprinting
    - Audio fingerprinting
    - Font fingerprinting
    - Screen properties

    Example:
        >>> class CanvasFingerprintPlugin(FingerprintPlugin):
        ...     name = "fingerprint.canvas"
        ...     priority = 50
        ...
        ...     async def apply(self, context):
        ...         # Modify canvas rendering to create unique fingerprint
        ...         await context.add_init_script('''
        ...             const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;
        ...             // ... fingerprint modification logic
        ...         ''')
    """

    pass


class BehaviorPlugin(Plugin):
    """Base class for human behavior emulation plugins.

    Behavior plugins add human-like patterns to browser interactions,
    making automated actions appear more natural.

    Examples of behavior plugins:
    - Random delays between actions
    - Mouse movement patterns
    - Scrolling behavior
    - Typing patterns
    - Random interactions

    Example:
        >>> class DelayBehaviorPlugin(BehaviorPlugin):
        ...     name = "behavior.delays"
        ...     priority = 200
        ...
        ...     async def apply(self, context):
        ...         # Store configuration for delays
        ...         context._phantom_delays = {"min": 0.3, "max": 1.5}
        ...
        ...     async def apply_to_page(self, page):
        ...         # Add delay before each action
        ...         import random
        ...         import asyncio
        ...         delays = page.context._phantom_delays
        ...         await asyncio.sleep(random.uniform(delays["min"], delays["max"]))
    """

    pass


__all__ = [
    "Plugin",
    "StealthPlugin",
    "FingerprintPlugin",
    "BehaviorPlugin",
]
