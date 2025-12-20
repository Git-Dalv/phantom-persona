"""Browser management for phantom-persona.

This module provides the BrowserManager class for managing Playwright
browser lifecycle, including starting, stopping, and configuration.
"""

from typing import TYPE_CHECKING, Any, Optional

from playwright.async_api import async_playwright

from phantom_persona.config.schema import BrowserConfig
from phantom_persona.core.exceptions import BrowserException, BrowserLaunchError

if TYPE_CHECKING:
    from playwright.async_api import Browser, Playwright


class BrowserManager:
    """Manager for Playwright browser lifecycle.

    Handles starting and stopping Playwright browsers with proper
    configuration and cleanup. Supports async context manager pattern
    for automatic resource management.

    Attributes:
        browser_type: Browser type to launch ("chromium", "firefox", "webkit")
        config: Browser configuration settings

    Example:
        >>> config = BrowserConfig(headless=True)
        >>> manager = BrowserManager(browser_type="chromium", config=config)
        >>> await manager.start()
        >>> browser = manager.browser
        >>> await manager.close()

        >>> # Or use as context manager
        >>> async with BrowserManager("chromium", config) as manager:
        ...     browser = manager.browser
        ...     # Browser automatically closed on exit
    """

    def __init__(
        self,
        browser_type: str = "chromium",
        config: Optional[BrowserConfig] = None,
    ) -> None:
        """Initialize browser manager.

        Args:
            browser_type: Browser type ("chromium", "firefox", "webkit")
            config: Browser configuration (uses defaults if None)

        Example:
            >>> manager = BrowserManager("chromium")
            >>> manager = BrowserManager("firefox", BrowserConfig(headless=False))
        """
        self.browser_type = browser_type
        self.config = config or BrowserConfig()
        self._playwright: Optional["Playwright"] = None
        self._browser: Optional["Browser"] = None

    async def start(self) -> "Browser":
        """Start Playwright and launch browser.

        Initializes Playwright, gets the appropriate browser launcher,
        and launches the browser with configured arguments.

        Returns:
            Launched browser instance

        Raises:
            BrowserLaunchError: If browser fails to launch

        Example:
            >>> manager = BrowserManager("chromium")
            >>> browser = await manager.start()
            >>> print(browser.is_connected())
            True
        """
        try:
            # Start Playwright
            self._playwright = await async_playwright().start()

            # Get browser launcher (chromium, firefox, or webkit)
            launcher = getattr(self._playwright, self.browser_type)

            # Build launch arguments from config
            launch_args = self._build_launch_args()

            # Launch browser
            self._browser = await launcher.launch(**launch_args)

            return self._browser

        except AttributeError as e:
            raise BrowserLaunchError(
                f"Invalid browser type: {self.browser_type}",
                details={
                    "browser_type": self.browser_type,
                    "valid_types": ["chromium", "firefox", "webkit"],
                },
            ) from e
        except Exception as e:
            raise BrowserLaunchError(
                f"Failed to launch {self.browser_type} browser",
                details={
                    "browser_type": self.browser_type,
                    "error": str(e),
                },
            ) from e

    async def close(self) -> None:
        """Close browser and stop Playwright.

        Properly shuts down the browser and Playwright instances,
        releasing all resources. Safe to call multiple times.

        Example:
            >>> await manager.start()
            >>> # Use browser...
            >>> await manager.close()
        """
        if self._browser:
            try:
                await self._browser.close()
            except Exception:
                # Ignore errors during cleanup
                pass
            finally:
                self._browser = None

        if self._playwright:
            try:
                await self._playwright.stop()
            except Exception:
                # Ignore errors during cleanup
                pass
            finally:
                self._playwright = None

    def _build_launch_args(self) -> dict[str, Any]:
        """Build browser launch arguments from configuration.

        Converts BrowserConfig settings into Playwright launch arguments.

        Returns:
            Dictionary of launch arguments for Playwright

        Example:
            >>> manager = BrowserManager("chromium")
            >>> args = manager._build_launch_args()
            >>> print(args)
            {'headless': True, 'slow_mo': 0}
        """
        args: dict[str, Any] = {
            "headless": self.config.headless,
            "slow_mo": self.config.slow_mo,
        }

        # Add custom browser arguments if specified
        if self.config.args:
            args["args"] = self.config.args

        return args

    @property
    def browser(self) -> "Browser":
        """Get the browser instance.

        Returns:
            Active browser instance

        Raises:
            BrowserException: If browser has not been started

        Example:
            >>> await manager.start()
            >>> browser = manager.browser
            >>> context = await browser.new_context()
        """
        if not self._browser:
            raise BrowserException(
                "Browser not started. Call start() first.",
                details={"browser_type": self.browser_type},
            )
        return self._browser

    @property
    def is_running(self) -> bool:
        """Check if browser is currently running.

        Returns:
            True if browser is running, False otherwise

        Example:
            >>> manager = BrowserManager("chromium")
            >>> print(manager.is_running)
            False
            >>> await manager.start()
            >>> print(manager.is_running)
            True
        """
        return self._browser is not None and self._browser.is_connected()

    async def __aenter__(self) -> "BrowserManager":
        """Enter async context manager.

        Automatically starts the browser when entering context.

        Returns:
            Self (BrowserManager instance)

        Example:
            >>> async with BrowserManager("chromium") as manager:
            ...     browser = manager.browser
            ...     # Browser is automatically started
        """
        await self.start()
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Exit async context manager.

        Automatically closes the browser when exiting context,
        even if an exception occurred.

        Args:
            *args: Exception info (if any)

        Example:
            >>> async with BrowserManager("chromium") as manager:
            ...     browser = manager.browser
            ...     # Browser automatically closed here
        """
        await self.close()

    def __repr__(self) -> str:
        """String representation of browser manager.

        Returns:
            Formatted string with browser type and status

        Example:
            >>> manager = BrowserManager("chromium")
            >>> repr(manager)
            '<BrowserManager browser_type=chromium running=False>'
        """
        return (
            f"<BrowserManager browser_type={self.browser_type} "
            f"running={self.is_running}>"
        )


__all__ = ["BrowserManager"]
