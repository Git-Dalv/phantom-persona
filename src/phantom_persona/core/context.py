"""Browser context management with persona settings.

This module provides builders and managers for creating Playwright browser
contexts configured with persona fingerprints, proxy settings, and plugins.
"""

from typing import TYPE_CHECKING, Any, Optional

from phantom_persona.core.exceptions import BrowserContextError

if TYPE_CHECKING:
    from playwright.async_api import Browser, BrowserContext

    from phantom_persona.persona.identity import Persona
    from phantom_persona.plugins.base import Plugin
    from phantom_persona.proxy.models import ProxyInfo


class ContextBuilder:
    """Builder for browser context with persona settings.

    Uses the fluent builder pattern to construct browser context options
    from persona configuration, proxy settings, and storage state.

    Example:
        >>> builder = ContextBuilder(browser)
        >>> builder.with_persona(persona).with_proxy(proxy)
        >>> context = await builder.build()
    """

    def __init__(self, browser: "Browser") -> None:
        """Initialize context builder.

        Args:
            browser: Playwright browser instance

        Example:
            >>> builder = ContextBuilder(browser)
        """
        self._browser = browser
        self._options: dict[str, Any] = {}

    def with_persona(self, persona: "Persona") -> "ContextBuilder":
        """Apply persona settings to context.

        Configures user agent, viewport, locale, timezone, and device
        characteristics from the persona's fingerprint and geo info.

        Args:
            persona: Persona with fingerprint and geo information

        Returns:
            Self for method chaining

        Example:
            >>> builder.with_persona(persona)
            >>> # User agent, viewport, locale all configured
        """
        # User agent from fingerprint
        self._options["user_agent"] = persona.fingerprint.user_agent

        # Viewport from device settings
        self._options["viewport"] = {
            "width": persona.fingerprint.device.screen_width,
            "height": persona.fingerprint.device.screen_height,
        }

        # Locale and timezone from geo
        self._options["locale"] = persona.geo.language
        self._options["timezone_id"] = persona.geo.timezone

        # Color scheme (could be from persona in future)
        self._options["color_scheme"] = "light"

        # Device scale factor
        self._options["device_scale_factor"] = persona.fingerprint.device.pixel_ratio

        # Geolocation - currently disabled, can be set from proxy geo in future
        self._options["geolocation"] = None
        self._options["permissions"] = ["geolocation"]

        return self

    def with_proxy(self, proxy: "ProxyInfo") -> "ContextBuilder":
        """Add proxy configuration to context.

        Args:
            proxy: Proxy configuration with server, auth, etc.

        Returns:
            Self for method chaining

        Example:
            >>> builder.with_proxy(proxy_info)
        """
        self._options["proxy"] = proxy.playwright_proxy
        return self

    def with_storage_state(self, state: dict[str, Any]) -> "ContextBuilder":
        """Restore cookies and localStorage from storage state.

        Args:
            state: Storage state dictionary with cookies and origins

        Returns:
            Self for method chaining

        Example:
            >>> state = {"cookies": [...], "origins": [...]}
            >>> builder.with_storage_state(state)
        """
        self._options["storage_state"] = state
        return self

    def with_options(self, **options: Any) -> "ContextBuilder":
        """Add custom context options.

        Allows setting additional Playwright context options not
        covered by other methods.

        Args:
            **options: Additional context options

        Returns:
            Self for method chaining

        Example:
            >>> builder.with_options(
            ...     ignore_https_errors=True,
            ...     extra_http_headers={"X-Custom": "value"}
            ... )
        """
        self._options.update(options)
        return self

    async def build(self) -> "BrowserContext":
        """Create browser context with configured options.

        Returns:
            Configured Playwright browser context

        Raises:
            BrowserContextError: If context creation fails

        Example:
            >>> context = await builder.build()
            >>> page = await context.new_page()
        """
        try:
            return await self._browser.new_context(**self._options)
        except Exception as e:
            raise BrowserContextError(
                "Failed to create browser context",
                details={"options": self._options, "error": str(e)},
            ) from e

    def get_options(self) -> dict[str, Any]:
        """Get current context options.

        Returns:
            Dictionary of context options

        Example:
            >>> options = builder.get_options()
            >>> print(options["user_agent"])
        """
        return self._options.copy()


class ContextManager:
    """Manager for browser context with plugin application.

    Handles the full lifecycle of a browser context including creation,
    plugin application, and cleanup with storage state preservation.

    Example:
        >>> manager = ContextManager(browser, persona, plugins)
        >>> context = await manager.create()
        >>> # Use context...
        >>> storage = await manager.close()
    """

    def __init__(
        self,
        browser: "Browser",
        persona: "Persona",
        plugins: list["Plugin"],
        browser_type: str = "chromium",
    ) -> None:
        """Initialize context manager.

        Args:
            browser: Playwright browser instance
            persona: Persona configuration
            plugins: List of plugins to apply
            browser_type: Browser type (chromium, firefox, webkit)

        Example:
            >>> plugins = registry.get_for_level(ProtectionLevel.MODERATE)
            >>> manager = ContextManager(browser, persona, plugins, "chromium")
        """
        self.browser = browser
        self.persona = persona
        self.plugins = plugins
        self.browser_type = browser_type
        self._context: Optional["BrowserContext"] = None

    async def create(self) -> "BrowserContext":
        """Create context and apply plugins.

        Builds the browser context with persona settings, proxy configuration,
        and storage state, then applies all plugins in priority order.

        Returns:
            Configured browser context with plugins applied

        Raises:
            BrowserContextError: If context creation or plugin application fails

        Example:
            >>> context = await manager.create()
            >>> page = await context.new_page()
        """
        # Build context with persona settings
        builder = ContextBuilder(self.browser)
        builder.with_persona(self.persona)

        # Add proxy if configured
        if self.persona.proxy:
            builder.with_proxy(self.persona.proxy)

        # Restore storage state if available
        if self.persona.cookies:
            # Convert persona cookies to Playwright storage state format
            storage_state = {
                "cookies": self.persona.cookies,
                "origins": [],  # Can add localStorage here if needed
            }
            builder.with_storage_state(storage_state)

        # Create context
        self._context = await builder.build()

        # Apply plugins in priority order (sorted by priority)
        try:
            for plugin in sorted(self.plugins, key=lambda p: p.priority):
                # Only apply if compatible with browser type
                if plugin.is_compatible(self.browser_type):
                    await plugin.apply(self._context)
        except Exception as e:
            # If plugin application fails, close context and raise
            await self._context.close()
            raise BrowserContextError(
                "Failed to apply plugins to context",
                details={"error": str(e)},
            ) from e

        return self._context

    async def close(self) -> dict[str, Any]:
        """Close context and return storage state.

        Saves cookies and localStorage before closing the context,
        allowing state to be restored in future sessions.

        Returns:
            Storage state dictionary with cookies and origins

        Example:
            >>> storage = await manager.close()
            >>> # Save storage to persona for next session
            >>> persona.cookies = storage.get("cookies", [])
        """
        storage: dict[str, Any] = {}

        if self._context:
            try:
                # Save storage state before closing
                storage = await self._context.storage_state()
            except Exception:
                # If storage state fails, return empty dict
                storage = {"cookies": [], "origins": []}
            finally:
                # Always try to close context
                try:
                    await self._context.close()
                except Exception:
                    # Ignore errors during cleanup
                    pass
                self._context = None

        return storage

    @property
    def context(self) -> "BrowserContext":
        """Get the browser context.

        Returns:
            Active browser context

        Raises:
            BrowserContextError: If context has not been created

        Example:
            >>> await manager.create()
            >>> context = manager.context
            >>> page = await context.new_page()
        """
        if not self._context:
            raise BrowserContextError(
                "Context not created. Call create() first.",
                details={"persona_id": self.persona.id},
            )
        return self._context

    @property
    def is_active(self) -> bool:
        """Check if context is currently active.

        Returns:
            True if context exists, False otherwise

        Example:
            >>> print(manager.is_active)
            False
            >>> await manager.create()
            >>> print(manager.is_active)
            True
        """
        return self._context is not None

    async def __aenter__(self) -> "ContextManager":
        """Enter async context manager.

        Automatically creates the context when entering.

        Returns:
            Self (ContextManager instance)

        Example:
            >>> async with ContextManager(browser, persona, plugins) as manager:
            ...     context = manager.context
        """
        await self.create()
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Exit async context manager.

        Automatically closes the context when exiting.

        Args:
            *args: Exception info (if any)

        Example:
            >>> async with ContextManager(...) as manager:
            ...     # Use context
            ...     pass
            ...     # Context automatically closed here
        """
        await self.close()

    def __repr__(self) -> str:
        """String representation of context manager.

        Returns:
            Formatted string with persona ID and status

        Example:
            >>> repr(manager)
            '<ContextManager persona=persona_123 active=True plugins=5>'
        """
        return (
            f"<ContextManager persona={self.persona.id} "
            f"active={self.is_active} plugins={len(self.plugins)}>"
        )


__all__ = ["ContextBuilder", "ContextManager"]
