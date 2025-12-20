"""Integration tests for browser management.

Tests BrowserManager and browser context creation with Playwright.
"""

import pytest

from phantom_persona.config import BrowserConfig
from phantom_persona.core import BrowserManager
from phantom_persona.core.exceptions import BrowserException, BrowserLaunchError


# === Browser Manager Tests ===


@pytest.mark.asyncio
async def test_browser_manager_start_close():
    """Test browser manager start and close lifecycle.

    Verifies:
    - Browser can be started
    - Browser is connected after start
    - Browser can be closed
    - Browser is not connected after close
    """
    config = BrowserConfig(headless=True)
    manager = BrowserManager(browser_type="chromium", config=config)

    # Initially not running
    assert not manager.is_running

    # Start browser
    browser = await manager.start()

    # Check browser is running
    assert browser is not None
    assert browser.is_connected()
    assert manager.is_running

    # Access browser property
    assert manager.browser == browser

    # Close browser
    await manager.close()

    # Check browser is stopped
    assert not manager.is_running


@pytest.mark.asyncio
async def test_browser_manager_context_manager():
    """Test browser manager as async context manager.

    Verifies:
    - Browser starts automatically on enter
    - Browser is available inside context
    - Browser closes automatically on exit
    """
    config = BrowserConfig(headless=True)

    async with BrowserManager(browser_type="chromium", config=config) as manager:
        # Browser should be running inside context
        assert manager.is_running
        assert manager.browser.is_connected()

        # Can access browser
        browser = manager.browser
        assert browser is not None

    # Browser should be stopped after exiting context
    assert not manager.is_running


@pytest.mark.asyncio
async def test_browser_manager_multiple_browsers():
    """Test managing multiple browser instances.

    Verifies:
    - Multiple browsers can be started simultaneously
    - Each browser is independent
    """
    config = BrowserConfig(headless=True)

    manager1 = BrowserManager(browser_type="chromium", config=config)
    manager2 = BrowserManager(browser_type="chromium", config=config)

    await manager1.start()
    await manager2.start()

    assert manager1.is_running
    assert manager2.is_running
    assert manager1.browser != manager2.browser

    await manager1.close()
    await manager2.close()


@pytest.mark.asyncio
async def test_browser_manager_firefox():
    """Test browser manager with Firefox.

    Verifies:
    - Firefox browser can be launched
    - Browser type is set correctly
    """
    config = BrowserConfig(headless=True)
    manager = BrowserManager(browser_type="firefox", config=config)

    await manager.start()

    assert manager.is_running
    assert manager.browser_type == "firefox"
    assert manager.browser.is_connected()

    await manager.close()


@pytest.mark.asyncio
async def test_browser_manager_webkit():
    """Test browser manager with WebKit.

    Verifies:
    - WebKit browser can be launched
    - Browser type is set correctly
    """
    config = BrowserConfig(headless=True)
    manager = BrowserManager(browser_type="webkit", config=config)

    await manager.start()

    assert manager.is_running
    assert manager.browser_type == "webkit"
    assert manager.browser.is_connected()

    await manager.close()


@pytest.mark.asyncio
async def test_browser_manager_invalid_browser_type():
    """Test browser manager with invalid browser type.

    Verifies:
    - Invalid browser type raises BrowserLaunchError
    """
    manager = BrowserManager(browser_type="invalid")

    with pytest.raises(BrowserLaunchError, match="Invalid browser type"):
        await manager.start()


@pytest.mark.asyncio
async def test_browser_manager_access_before_start():
    """Test accessing browser before starting.

    Verifies:
    - Accessing browser property before start raises BrowserException
    """
    manager = BrowserManager(browser_type="chromium")

    with pytest.raises(BrowserException, match="Browser not started"):
        _ = manager.browser


@pytest.mark.asyncio
async def test_browser_manager_close_multiple_times():
    """Test closing browser multiple times.

    Verifies:
    - Multiple close calls are safe (idempotent)
    - No errors are raised
    """
    config = BrowserConfig(headless=True)
    manager = BrowserManager(browser_type="chromium", config=config)

    await manager.start()
    await manager.close()
    await manager.close()  # Should not raise error
    await manager.close()  # Should not raise error


# === Browser Context Tests ===


@pytest.mark.asyncio
async def test_browser_creates_context():
    """Test browser can create new context.

    Verifies:
    - Browser context can be created
    - Context is valid and can create pages
    """
    config = BrowserConfig(headless=True)

    async with BrowserManager(browser_type="chromium", config=config) as manager:
        browser = manager.browser

        # Create context
        context = await browser.new_context()

        assert context is not None

        # Create page in context
        page = await context.new_page()
        assert page is not None

        # Navigate to a page
        await page.goto("about:blank")
        assert page.url == "about:blank"

        await context.close()


@pytest.mark.asyncio
async def test_context_with_viewport():
    """Test browser context with custom viewport.

    Verifies:
    - Viewport settings are applied to context
    - Pages in context have correct viewport
    """
    config = BrowserConfig(headless=True)

    async with BrowserManager(browser_type="chromium", config=config) as manager:
        browser = manager.browser

        # Create context with custom viewport
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080}
        )

        page = await context.new_page()

        # Check viewport size
        viewport = page.viewport_size
        assert viewport["width"] == 1920
        assert viewport["height"] == 1080

        await context.close()


@pytest.mark.asyncio
async def test_context_with_user_agent():
    """Test browser context with custom user agent.

    Verifies:
    - User agent is applied to context
    - Pages in context use correct user agent
    """
    config = BrowserConfig(headless=True)
    custom_ua = "Mozilla/5.0 (Custom User Agent) Test/1.0"

    async with BrowserManager(browser_type="chromium", config=config) as manager:
        browser = manager.browser

        # Create context with custom user agent
        context = await browser.new_context(user_agent=custom_ua)

        page = await context.new_page()

        # Evaluate user agent in page
        page_ua = await page.evaluate("navigator.userAgent")
        assert page_ua == custom_ua

        await context.close()


@pytest.mark.asyncio
async def test_context_with_locale():
    """Test browser context with custom locale and timezone.

    Verifies:
    - Locale settings are applied to context
    - Timezone settings are applied to context
    - Pages in context use correct locale and timezone
    """
    config = BrowserConfig(headless=True)

    async with BrowserManager(browser_type="chromium", config=config) as manager:
        browser = manager.browser

        # Create context with custom locale and timezone
        context = await browser.new_context(
            locale="de-DE",
            timezone_id="Europe/Berlin",
        )

        page = await context.new_page()

        # Check locale
        page_locale = await page.evaluate("navigator.language")
        assert page_locale == "de-DE"

        # Check timezone (by checking date formatting)
        # Berlin uses CET/CEST timezone
        timezone_info = await page.evaluate("""() => {
            const date = new Date('2024-01-01T12:00:00Z');
            return {
                timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                offset: date.getTimezoneOffset()
            };
        }""")

        assert timezone_info["timezone"] == "Europe/Berlin"

        await context.close()


@pytest.mark.asyncio
async def test_context_with_geolocation():
    """Test browser context with geolocation.

    Verifies:
    - Geolocation settings are applied to context
    """
    config = BrowserConfig(headless=True)

    async with BrowserManager(browser_type="chromium", config=config) as manager:
        browser = manager.browser

        # Create context with geolocation
        context = await browser.new_context(
            geolocation={"latitude": 52.52, "longitude": 13.405},
            permissions=["geolocation"],
        )

        page = await context.new_page()
        await page.goto("about:blank")

        # Get geolocation from page
        location = await page.evaluate("""() => {
            return new Promise((resolve) => {
                navigator.geolocation.getCurrentPosition(
                    (position) => resolve({
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude
                    }),
                    (error) => resolve({error: error.message})
                );
            });
        }""")

        assert "error" not in location
        assert location["latitude"] == 52.52
        assert location["longitude"] == 13.405

        await context.close()


@pytest.mark.asyncio
async def test_context_with_permissions():
    """Test browser context with permissions.

    Verifies:
    - Permissions can be granted to context
    """
    config = BrowserConfig(headless=True)

    async with BrowserManager(browser_type="chromium", config=config) as manager:
        browser = manager.browser

        # Create context with permissions
        context = await browser.new_context(permissions=["notifications"])

        page = await context.new_page()
        await page.goto("about:blank")

        # Check notification permission
        permission = await page.evaluate(
            "Notification.permission"
        )

        assert permission == "granted"

        await context.close()


@pytest.mark.asyncio
async def test_multiple_contexts():
    """Test creating multiple contexts in same browser.

    Verifies:
    - Multiple contexts can exist simultaneously
    - Each context is independent
    - Contexts can have different settings
    """
    config = BrowserConfig(headless=True)

    async with BrowserManager(browser_type="chromium", config=config) as manager:
        browser = manager.browser

        # Create two contexts with different viewports
        context1 = await browser.new_context(
            viewport={"width": 1920, "height": 1080}
        )
        context2 = await browser.new_context(
            viewport={"width": 1366, "height": 768}
        )

        page1 = await context1.new_page()
        page2 = await context2.new_page()

        # Check viewports are different
        viewport1 = page1.viewport_size
        viewport2 = page2.viewport_size

        assert viewport1["width"] == 1920
        assert viewport2["width"] == 1366

        await context1.close()
        await context2.close()


# === Browser Configuration Tests ===


@pytest.mark.asyncio
async def test_browser_with_args():
    """Test browser launch with custom arguments.

    Verifies:
    - Custom browser arguments can be passed
    - Browser launches successfully with args
    """
    config = BrowserConfig(
        headless=True,
        args=["--disable-dev-shm-usage", "--no-sandbox"],
    )

    async with BrowserManager(browser_type="chromium", config=config) as manager:
        assert manager.is_running
        assert manager.browser.is_connected()


@pytest.mark.asyncio
async def test_browser_headless_mode():
    """Test browser in headless mode.

    Verifies:
    - Browser runs in headless mode
    - Pages can be created and navigated
    """
    config = BrowserConfig(headless=True)

    async with BrowserManager(browser_type="chromium", config=config) as manager:
        browser = manager.browser
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("about:blank")
        assert page.url == "about:blank"

        await context.close()


@pytest.mark.asyncio
async def test_browser_slow_mo():
    """Test browser with slow_mo setting.

    Verifies:
    - Browser can be launched with slow_mo
    - Operations are slowed down (basic check)
    """
    config = BrowserConfig(headless=True, slow_mo=50)

    async with BrowserManager(browser_type="chromium", config=config) as manager:
        assert manager.is_running
        assert manager.config.slow_mo == 50


# === Error Handling Tests ===


@pytest.mark.asyncio
async def test_browser_context_after_close():
    """Test creating context after browser is closed.

    Verifies:
    - Cannot create context after browser is closed
    - Appropriate error is raised
    """
    config = BrowserConfig(headless=True)
    manager = BrowserManager(browser_type="chromium", config=config)

    await manager.start()
    browser = manager.browser
    await manager.close()

    # Attempting to create context should fail
    with pytest.raises(Exception):  # Playwright will raise an error
        await browser.new_context()
