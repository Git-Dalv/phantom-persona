"""Main client for phantom-persona library.

This module provides the PhantomPersona class, which is the primary entry point
for using the library. It orchestrates browser management, plugin loading,
and session creation.
"""

from pathlib import Path
from typing import Any, Optional, Union
from uuid import uuid4

from phantom_persona.config import ConfigLoader, PhantomConfig, ProtectionLevel
from phantom_persona.core import BrowserManager, ContextManager, Session
from phantom_persona.core.exceptions import PhantomException
from phantom_persona.persona import DeviceInfo, Fingerprint, GeoInfo, Persona
from phantom_persona.plugins import registry
from phantom_persona.proxy import ProxyInfo


class PhantomPersona:
    """Main client for browser automation with anti-detection.

    High-level API that orchestrates all components: browser management,
    plugin loading, persona handling, and session creation. Provides
    convenient methods for creating browser sessions with varying levels
    of protection.

    Attributes:
        config: Configuration settings
        browser_type: Browser type to use (chromium, firefox, webkit)
        plugins: List of loaded plugins

    Example:
        >>> # Basic usage with protection level
        >>> async with PhantomPersona(level=2) as client:
        ...     session = await client.new_session()
        ...     page = await session.new_page()
        ...     await page.goto("https://example.com")

        >>> # Advanced usage with custom config
        >>> config = ConfigLoader.load("config.yaml")
        >>> client = PhantomPersona.from_config(config)
        >>> await client.start()
        >>> session = await client.new_session(persona=my_persona)
    """

    def __init__(
        self,
        level: Optional[int] = None,
        config: Optional[PhantomConfig] = None,
        browser_type: str = "chromium",
    ) -> None:
        """Initialize PhantomPersona client.

        Args:
            level: Protection level (0-4). Ignored if config is provided.
            config: Custom configuration. If None, uses level or defaults.
            browser_type: Browser type ("chromium", "firefox", "webkit")

        Raises:
            PhantomException: If neither level nor config is provided

        Example:
            >>> client = PhantomPersona(level=2)
            >>> client = PhantomPersona(config=my_config, browser_type="firefox")
        """
        # Determine configuration
        if config is not None:
            self.config = config
        elif level is not None:
            self.config = ConfigLoader.from_level(level)
        else:
            # Default to level 1 (BASIC)
            self.config = ConfigLoader.from_level(1)

        self.browser_type = browser_type
        self._browser_manager: Optional[BrowserManager] = None
        self._started = False

    async def start(self) -> None:
        """Start the client and initialize browser.

        Performs plugin auto-discovery and starts the browser manager.
        Must be called before creating sessions (unless using context manager).

        Raises:
            PhantomException: If client is already started
            BrowserLaunchError: If browser fails to launch

        Example:
            >>> client = PhantomPersona(level=2)
            >>> await client.start()
            >>> # Now ready to create sessions
        """
        if self._started:
            raise PhantomException(
                "Client already started",
                details={"browser_type": self.browser_type},
            )

        # Auto-discover plugins
        registry.autodiscover()

        # Start browser manager
        self._browser_manager = BrowserManager(
            browser_type=self.browser_type,
            config=self.config.browser,
        )
        await self._browser_manager.start()

        self._started = True

    async def close(self) -> None:
        """Close the client and cleanup resources.

        Stops the browser and releases all resources. Safe to call
        multiple times.

        Example:
            >>> await client.start()
            >>> # Use client...
            >>> await client.close()
        """
        if self._browser_manager:
            await self._browser_manager.close()
            self._browser_manager = None
        self._started = False

    async def new_session(
        self,
        persona: Optional[Persona] = None,
        proxy: Optional[ProxyInfo] = None,
    ) -> Session:
        """Create a new browser session with persona.

        Creates a browser context configured with the persona's fingerprint,
        applies all plugins for the configured protection level, and returns
        a high-level Session object.

        Args:
            persona: Persona to use. If None, creates a default persona.
            proxy: Proxy configuration. Overrides persona.proxy if provided.

        Returns:
            New session ready for automation

        Raises:
            PhantomException: If client is not started
            BrowserContextError: If context creation fails

        Example:
            >>> session = await client.new_session()
            >>> page = await session.new_page()
            >>> await page.goto("https://example.com")
            >>> await session.close()
        """
        if not self._started or not self._browser_manager:
            raise PhantomException(
                "Client not started. Call start() first or use context manager.",
                details={"browser_type": self.browser_type},
            )

        # Create default persona if not provided
        if persona is None:
            persona = self._create_default_persona()

        # Override proxy if provided
        if proxy is not None:
            persona.proxy = proxy

        # Get plugins for protection level
        plugins = registry.get_for_level(
            level=self.config.level,
            browser_type=self.browser_type,
        )

        # Create context manager and context
        context_manager = ContextManager(
            browser=self._browser_manager.browser,
            persona=persona,
            plugins=plugins,
        )
        context = await context_manager.create()

        # Create and return session
        session = Session(
            context=context,
            persona=persona,
            behavior_config=self.config.behavior,
        )

        return session

    def _create_default_persona(self) -> Persona:
        """Create a default persona with reasonable settings.

        Returns:
            Basic persona with US geo and Chrome fingerprint

        Example:
            >>> persona = client._create_default_persona()
            >>> print(persona.geo.country)
            United States
        """
        from datetime import datetime

        # Default geo info
        geo = GeoInfo(
            country_code="US",
            country="United States",
            city="San Francisco",
            timezone="America/Los_Angeles",
            language="en-US",
            languages=["en-US", "en"],
        )

        # Default device info
        device = DeviceInfo(
            type="desktop",
            platform="Win32",
            vendor="Google Inc.",
            renderer="ANGLE (Intel, Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0)",
            screen_width=1920,
            screen_height=1080,
            color_depth=24,
            pixel_ratio=1.0,
        )

        # Default fingerprint
        fingerprint = Fingerprint(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            device=device,
            canvas_hash=f"canvas_{uuid4().hex[:12]}",
            audio_hash=f"audio_{uuid4().hex[:12]}",
        )

        # Create persona
        persona = Persona(
            fingerprint=fingerprint,
            geo=geo,
            created_at=datetime.now(),
        )

        return persona

    async def new_page(
        self,
        persona: Optional[Persona] = None,
        proxy: Optional[ProxyInfo] = None,
    ) -> "Page":
        """Convenience method to create a session and get a page.

        Creates a new session and immediately creates a page in it.
        Note: You won't have direct access to the session object,
        so use new_session() if you need session-level control.

        Args:
            persona: Persona to use
            proxy: Proxy configuration

        Returns:
            New page ready for automation

        Example:
            >>> page = await client.new_page()
            >>> await page.goto("https://example.com")
        """
        session = await self.new_session(persona=persona, proxy=proxy)
        return await session.new_page()

    @classmethod
    def from_config(
        cls,
        config_path: Union[str, Path],
        browser_type: str = "chromium",
    ) -> "PhantomPersona":
        """Create client from configuration file.

        Loads configuration from YAML or JSON file and creates
        a PhantomPersona instance.

        Args:
            config_path: Path to config file (YAML or JSON)
            browser_type: Browser type to use

        Returns:
            Configured PhantomPersona instance

        Raises:
            ConfigException: If config file is invalid

        Example:
            >>> client = PhantomPersona.from_config("config.yaml")
            >>> await client.start()
        """
        config = ConfigLoader.load(config_path)
        return cls(config=config, browser_type=browser_type)

    # === Context manager support ===

    async def __aenter__(self) -> "PhantomPersona":
        """Enter async context manager.

        Automatically starts the client when entering context.

        Returns:
            Self (PhantomPersona instance)

        Example:
            >>> async with PhantomPersona(level=2) as client:
            ...     session = await client.new_session()
        """
        await self.start()
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Exit async context manager.

        Automatically closes the client when exiting context.

        Args:
            *args: Exception info (if any)

        Example:
            >>> async with PhantomPersona(level=2) as client:
            ...     # Use client
            ...     pass
            ...     # Automatically closed here
        """
        await self.close()

    # === Properties ===

    @property
    def is_started(self) -> bool:
        """Check if client is started.

        Returns:
            True if client is started, False otherwise

        Example:
            >>> print(client.is_started)
            False
            >>> await client.start()
            >>> print(client.is_started)
            True
        """
        return self._started

    @property
    def plugins(self) -> list[str]:
        """Get list of plugin names for current protection level.

        Returns:
            List of plugin names that will be applied

        Example:
            >>> print(client.plugins)
            ['stealth.basic', 'fingerprint.navigator']
        """
        if not self._started:
            return []

        plugins = registry.get_for_level(
            level=self.config.level,
            browser_type=self.browser_type,
        )
        return [p.name for p in plugins]

    def __repr__(self) -> str:
        """String representation of client.

        Returns:
            Formatted string with config and status

        Example:
            >>> repr(client)
            '<PhantomPersona level=2 browser=chromium started=True>'
        """
        return (
            f"<PhantomPersona level={self.config.level} "
            f"browser={self.browser_type} started={self._started}>"
        )


__all__ = ["PhantomPersona"]
