"""Session management for browser automation.

This module provides the Session class which combines browser context,
persona, and human-like behavior into a convenient high-level API.
"""

import asyncio
import random
from typing import TYPE_CHECKING, Any, Optional

from phantom_persona.config.schema import BehaviorConfig
from phantom_persona.core.exceptions import SessionError

if TYPE_CHECKING:
    from playwright.async_api import BrowserContext, Page

    from phantom_persona.persona.identity import Persona


class Session:
    """Browser session with persona and human-like behavior.

    Combines browser context, persona, and behavior configuration into
    a single high-level interface for browser automation. Provides
    convenience methods for human-like interactions and automatic state
    management.

    Attributes:
        context: Playwright browser context
        persona: Persona with fingerprint and geo settings
        behavior: Behavior configuration for human-like actions

    Example:
        >>> session = Session(context, persona)
        >>> page = await session.new_page()
        >>> await session.human_click(page, "#button")
        >>> await session.close()
    """

    def __init__(
        self,
        context: "BrowserContext",
        persona: "Persona",
        behavior_config: Optional[BehaviorConfig] = None,
    ) -> None:
        """Initialize session with context and persona.

        Args:
            context: Playwright browser context
            persona: Persona configuration
            behavior_config: Behavior settings (uses defaults if None)

        Example:
            >>> session = Session(context, persona)
            >>> session = Session(context, persona, BehaviorConfig(human_delays=True))
        """
        self.context = context
        self.persona = persona
        self.behavior = behavior_config or BehaviorConfig()
        self._pages: list["Page"] = []
        self._closed: bool = False

    async def new_page(self) -> "Page":
        """Create a new page in this session.

        Returns:
            New page instance

        Raises:
            SessionError: If session is closed

        Example:
            >>> page = await session.new_page()
            >>> await page.goto("https://example.com")
        """
        if self._closed:
            raise SessionError(
                "Cannot create page on closed session",
                details={"persona_id": self.persona.id, "state": "closed"},
            )

        page = await self.context.new_page()
        self._pages.append(page)
        return page

    async def close(self) -> None:
        """Close session and update persona.

        Saves cookies to persona, marks persona as used, and closes
        the browser context. Safe to call multiple times.

        Example:
            >>> await session.close()
            >>> # Cookies saved to persona, use_count incremented
        """
        if self._closed:
            return

        # Save cookies to persona
        try:
            cookies = await self.context.cookies()
            self.persona.cookies = cookies  # type: ignore
        except Exception:
            # Ignore errors during cookie extraction
            pass

        # Mark persona as used
        self.persona.mark_used()

        # Close context
        try:
            await self.context.close()
        except Exception:
            # Ignore errors during cleanup
            pass
        finally:
            self._closed = True

    # === Convenience methods with human-like behavior ===

    async def human_delay(
        self,
        min_sec: Optional[float] = None,
        max_sec: Optional[float] = None,
    ) -> None:
        """Add a human-like delay.

        Uses random delay between min and max seconds. If not specified,
        uses values from behavior configuration.

        Args:
            min_sec: Minimum delay in seconds (uses config if None)
            max_sec: Maximum delay in seconds (uses config if None)

        Example:
            >>> await session.human_delay()  # Uses config defaults
            >>> await session.human_delay(0.5, 1.5)  # Custom range
        """
        if not self.behavior.human_delays:
            return

        min_s = min_sec if min_sec is not None else self.behavior.delay_range[0]
        max_s = max_sec if max_sec is not None else self.behavior.delay_range[1]

        delay = random.uniform(min_s, max_s)
        await asyncio.sleep(delay)

    async def human_type(
        self,
        page: "Page",
        selector: str,
        text: str,
        delay_range: tuple[float, float] = (0.05, 0.15),
    ) -> None:
        """Type text with human-like speed.

        Types each character individually with random delays between
        keystrokes to simulate realistic typing.

        Args:
            page: Page to type on
            selector: CSS selector for input element
            text: Text to type
            delay_range: Min and max delay between characters in seconds

        Raises:
            SessionError: If session is closed

        Example:
            >>> await session.human_type(page, "#username", "john@example.com")
            >>> await session.human_type(page, "#search", "query", (0.1, 0.2))
        """
        if self._closed:
            raise SessionError(
                "Cannot perform actions on closed session",
                details={"persona_id": self.persona.id},
            )

        element = await page.wait_for_selector(selector)
        if element is None:
            return

        for char in text:
            await element.type(char)
            if self.behavior.human_delays:
                await asyncio.sleep(random.uniform(*delay_range))

    async def human_click(
        self,
        page: "Page",
        selector: str,
    ) -> None:
        """Click element with human-like delay before clicking.

        Adds a small random delay before clicking to simulate
        realistic user interaction.

        Args:
            page: Page to click on
            selector: CSS selector for element to click

        Raises:
            SessionError: If session is closed

        Example:
            >>> await session.human_click(page, "#submit-button")
        """
        if self._closed:
            raise SessionError(
                "Cannot perform actions on closed session",
                details={"persona_id": self.persona.id},
            )

        # Small delay before clicking
        await self.human_delay(0.1, 0.3)
        await page.click(selector)

    async def human_scroll(
        self,
        page: "Page",
        distance: int = 300,
    ) -> None:
        """Scroll page with human-like behavior.

        Scrolls the page by the specified distance with a delay.

        Args:
            page: Page to scroll
            distance: Pixels to scroll (positive = down, negative = up)

        Raises:
            SessionError: If session is closed

        Example:
            >>> await session.human_scroll(page, 500)  # Scroll down
            >>> await session.human_scroll(page, -300)  # Scroll up
        """
        if self._closed:
            raise SessionError(
                "Cannot perform actions on closed session",
                details={"persona_id": self.persona.id},
            )

        await page.evaluate(f"window.scrollBy(0, {distance})")
        await self.human_delay(0.2, 0.5)

    # === Context manager ===

    async def __aenter__(self) -> "Session":
        """Enter async context manager.

        Returns:
            Self (Session instance)

        Example:
            >>> async with Session(context, persona) as session:
            ...     page = await session.new_page()
        """
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Exit async context manager.

        Automatically closes the session when exiting.

        Args:
            *args: Exception info (if any)

        Example:
            >>> async with Session(context, persona) as session:
            ...     # Use session
            ...     pass
            ...     # Session automatically closed here
        """
        await self.close()

    # === Properties ===

    @property
    def page(self) -> "Page":
        """Get the last created page.

        Returns:
            Most recently created page

        Raises:
            SessionError: If no pages have been created

        Example:
            >>> page = await session.new_page()
            >>> # Later...
            >>> same_page = session.page
        """
        if not self._pages:
            raise SessionError(
                "No pages created in this session",
                details={"persona_id": self.persona.id},
            )
        return self._pages[-1]

    @property
    def pages(self) -> list["Page"]:
        """Get all pages in this session.

        Returns:
            List of all pages created in this session

        Example:
            >>> pages = session.pages
            >>> print(f"Session has {len(pages)} pages")
        """
        return self._pages.copy()

    @property
    def is_closed(self) -> bool:
        """Check if session is closed.

        Returns:
            True if session is closed, False otherwise

        Example:
            >>> print(session.is_closed)
            False
            >>> await session.close()
            >>> print(session.is_closed)
            True
        """
        return self._closed

    def __repr__(self) -> str:
        """String representation of session.

        Returns:
            Formatted string with persona ID and status

        Example:
            >>> repr(session)
            '<Session persona=persona_123 pages=2 closed=False>'
        """
        return (
            f"<Session persona={self.persona.id} "
            f"pages={len(self._pages)} closed={self._closed}>"
        )


__all__ = ["Session"]
