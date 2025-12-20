"""End-to-end tests for bot detection evasion.

Tests anti-detection capabilities on real websites that detect bots.
Requires internet connection and Playwright browsers installed.
"""

import pytest

from phantom_persona import PhantomPersona, ProtectionLevel


@pytest.mark.e2e
@pytest.mark.asyncio
class TestDetection:
    """E2E tests for bot detection evasion.

    Tests the library's ability to bypass common bot detection methods
    used by popular detection websites.

    Note:
        These tests require:
        - Internet connection
        - Playwright browsers installed
        - May be slow due to page loads
        - May fail if websites change their detection methods
    """

    @pytest.mark.slow
    async def test_bot_sannysoft(self):
        """Test bot detection evasion on bot.sannysoft.com.

        Verifies:
        - webdriver property is undefined or false
        - navigator.webdriver is false/undefined
        - Basic bot detection tests are passed
        - No obvious automation indicators

        Website: https://bot.sannysoft.com
        Tests checked:
        - WebDriver presence
        - Chrome detection
        - Navigator properties
        - Plugin detection
        """
        async with PhantomPersona(level=ProtectionLevel.BASIC) as client:
            # Create session
            session = await client.new_session()
            page = await session.new_page()

            try:
                # Navigate to bot detection site
                await page.goto(
                    "https://bot.sannysoft.com",
                    wait_until="networkidle",
                    timeout=30000,
                )

                # Wait for detection tests to complete
                await page.wait_for_timeout(2000)

                # Check navigator.webdriver is false or undefined
                webdriver_value = await page.evaluate("navigator.webdriver")
                assert webdriver_value is False or webdriver_value is None, (
                    f"navigator.webdriver should be false/undefined, got: {webdriver_value}"
                )

                # Check window.navigator.webdriver
                window_webdriver = await page.evaluate("window.navigator.webdriver")
                assert window_webdriver is False or window_webdriver is None, (
                    f"window.navigator.webdriver should be false/undefined, got: {window_webdriver}"
                )

                # Check that webdriver is not in navigator
                has_webdriver = await page.evaluate(
                    "'webdriver' in navigator"
                )
                # It's OK if it's there but false, or not there at all
                if has_webdriver:
                    assert webdriver_value is False, (
                        "If webdriver property exists, it must be false"
                    )

                # Check Chrome object presence (should exist for Chrome-like browsers)
                has_chrome = await page.evaluate("typeof window.chrome !== 'undefined'")
                # For Chromium browser, chrome object should exist
                if "chromium" in client.browser_type.lower():
                    assert has_chrome, "Chrome object should exist for Chromium browser"

                # Check plugins (modern browsers may have 0 plugins, but should have the property)
                plugins_length = await page.evaluate("navigator.plugins.length")
                assert isinstance(plugins_length, int), "Plugins should be accessible"

                # Check languages array
                languages = await page.evaluate("navigator.languages")
                assert isinstance(languages, list) and len(languages) > 0, (
                    "Navigator languages should be a non-empty array"
                )

                # Check that permissions API exists
                has_permissions = await page.evaluate(
                    "typeof navigator.permissions !== 'undefined'"
                )
                assert has_permissions, "Permissions API should exist"

                # Additional checks for common bot indicators
                # Check that window.callPhantom doesn't exist (PhantomJS indicator)
                has_phantom = await page.evaluate("typeof window.callPhantom")
                assert has_phantom == "undefined", "PhantomJS indicators should not exist"

                # Check that __nightmare doesn't exist (Nightmare.js indicator)
                has_nightmare = await page.evaluate("typeof window.__nightmare")
                assert has_nightmare == "undefined", "Nightmare.js indicators should not exist"

                # Optionally, capture screenshot for manual verification
                # await page.screenshot(path="sannysoft_detection.png")

            finally:
                await session.close()

    @pytest.mark.slow
    async def test_browserleaks_navigator(self):
        """Test navigator properties on browserleaks.com/javascript.

        Verifies:
        - navigator.webdriver is false/undefined
        - navigator properties don't reveal automation
        - JavaScript execution environment looks normal
        - No automation-specific properties exposed

        Website: https://browserleaks.com/javascript
        Tests checked:
        - Navigator object properties
        - WebDriver detection
        - Automation indicators
        - JavaScript environment
        """
        async with PhantomPersona(level=ProtectionLevel.BASIC) as client:
            # Create session
            session = await client.new_session()
            page = await session.new_page()

            try:
                # Navigate to BrowserLeaks JavaScript test page
                await page.goto(
                    "https://browserleaks.com/javascript",
                    wait_until="networkidle",
                    timeout=30000,
                )

                # Wait for page to fully load and run tests
                await page.wait_for_timeout(3000)

                # Check navigator.webdriver
                webdriver_value = await page.evaluate("navigator.webdriver")
                assert webdriver_value is False or webdriver_value is None, (
                    f"navigator.webdriver should be false/undefined, got: {webdriver_value}"
                )

                # Check that common automation properties don't exist
                automation_checks = await page.evaluate("""() => {
                    return {
                        webdriver: navigator.webdriver,
                        hasWebdriver: 'webdriver' in navigator,
                        callPhantom: typeof window.callPhantom,
                        _phantom: typeof window._phantom,
                        nightmare: typeof window.__nightmare,
                        selenium: typeof window._selenium,
                        webdriverFunc: typeof document.documentElement.webdriver,
                        domAutomation: typeof window.domAutomation,
                        domAutomationController: typeof window.domAutomationController
                    };
                }""")

                # Verify no automation indicators
                assert automation_checks["webdriver"] is False or automation_checks["webdriver"] is None, (
                    "navigator.webdriver should be false or None"
                )
                assert automation_checks["callPhantom"] == "undefined", (
                    "PhantomJS indicators should not exist"
                )
                assert automation_checks["_phantom"] == "undefined", (
                    "PhantomJS indicators should not exist"
                )
                assert automation_checks["nightmare"] == "undefined", (
                    "Nightmare.js indicators should not exist"
                )
                assert automation_checks["selenium"] == "undefined", (
                    "Selenium indicators should not exist"
                )
                assert automation_checks["domAutomation"] == "undefined", (
                    "DOM automation indicators should not exist"
                )

                # Check navigator properties are realistic
                navigator_info = await page.evaluate("""() => {
                    return {
                        userAgent: navigator.userAgent,
                        platform: navigator.platform,
                        language: navigator.language,
                        languages: navigator.languages,
                        vendor: navigator.vendor,
                        hardwareConcurrency: navigator.hardwareConcurrency,
                        deviceMemory: navigator.deviceMemory,
                        maxTouchPoints: navigator.maxTouchPoints,
                        hasPlugins: typeof navigator.plugins !== 'undefined',
                        pluginsLength: navigator.plugins.length
                    };
                }""")

                # Verify navigator properties are set
                assert navigator_info["userAgent"], "User agent should be set"
                assert navigator_info["platform"], "Platform should be set"
                assert navigator_info["language"], "Language should be set"
                assert isinstance(navigator_info["languages"], list), "Languages should be an array"
                assert len(navigator_info["languages"]) > 0, "Languages should not be empty"

                # Check that vendor is set (typically "Google Inc." for Chromium)
                assert navigator_info["vendor"] is not None, "Vendor should be set"

                # Hardware concurrency should be a positive number
                if navigator_info["hardwareConcurrency"] is not None:
                    assert navigator_info["hardwareConcurrency"] > 0, (
                        "Hardware concurrency should be positive"
                    )

                # Plugins should be accessible
                assert navigator_info["hasPlugins"], "Plugins property should exist"
                assert isinstance(navigator_info["pluginsLength"], int), (
                    "Plugins length should be an integer"
                )

                # Check screen properties
                screen_info = await page.evaluate("""() => {
                    return {
                        width: screen.width,
                        height: screen.height,
                        availWidth: screen.availWidth,
                        availHeight: screen.availHeight,
                        colorDepth: screen.colorDepth,
                        pixelDepth: screen.pixelDepth
                    };
                }""")

                # Verify screen properties are realistic
                assert screen_info["width"] > 0, "Screen width should be positive"
                assert screen_info["height"] > 0, "Screen height should be positive"
                assert screen_info["colorDepth"] in [24, 30, 32], (
                    f"Color depth should be realistic, got: {screen_info['colorDepth']}"
                )

                # Check that Date and Math objects are not tampered
                date_check = await page.evaluate("typeof Date.prototype.getTimezoneOffset")
                assert date_check == "function", "Date object should be intact"

                math_check = await page.evaluate("typeof Math.random")
                assert math_check == "function", "Math object should be intact"

                # Optionally, capture screenshot for manual verification
                # await page.screenshot(path="browserleaks_detection.png")

            finally:
                await session.close()

    @pytest.mark.slow
    async def test_basic_stealth_features(self):
        """Test basic stealth features work correctly.

        Verifies:
        - Stealth plugins are applied
        - Basic anti-detection measures are in place
        - Browser appears as normal user browser

        This is a sanity check test that doesn't rely on external websites.
        """
        async with PhantomPersona(level=ProtectionLevel.BASIC) as client:
            session = await client.new_session()
            page = await session.new_page()

            try:
                # Navigate to blank page
                await page.goto("about:blank")

                # Check comprehensive automation indicators
                checks = await page.evaluate("""() => {
                    const results = {
                        // WebDriver checks
                        navigatorWebdriver: navigator.webdriver,
                        hasWebdriverProp: 'webdriver' in navigator,

                        // Chrome object
                        hasChrome: typeof window.chrome !== 'undefined',
                        hasChromeRuntime: typeof window.chrome?.runtime !== 'undefined',

                        // Permissions API
                        hasPermissions: typeof navigator.permissions !== 'undefined',

                        // Plugins
                        hasPlugins: typeof navigator.plugins !== 'undefined',
                        pluginsLength: navigator.plugins?.length || 0,

                        // Languages
                        hasLanguages: Array.isArray(navigator.languages),
                        languagesCount: navigator.languages?.length || 0,

                        // Automation frameworks
                        hasCallPhantom: typeof window.callPhantom !== 'undefined',
                        hasNightmare: typeof window.__nightmare !== 'undefined',
                        hasSelenium: typeof window._selenium !== 'undefined',
                        hasDomAutomation: typeof window.domAutomation !== 'undefined',

                        // User agent
                        userAgent: navigator.userAgent,

                        // Platform
                        platform: navigator.platform,
                    };

                    return results;
                }""")

                # Assert no automation indicators
                assert checks["navigatorWebdriver"] is False or checks["navigatorWebdriver"] is None, (
                    "navigator.webdriver should be false or undefined"
                )

                assert not checks["hasCallPhantom"], "PhantomJS indicators should not exist"
                assert not checks["hasNightmare"], "Nightmare.js indicators should not exist"
                assert not checks["hasSelenium"], "Selenium indicators should not exist"
                assert not checks["hasDomAutomation"], "DOM automation indicators should not exist"

                # Assert normal browser properties exist
                assert checks["hasPermissions"], "Permissions API should exist"
                assert checks["hasPlugins"], "Plugins should exist"
                assert checks["hasLanguages"], "Languages should be an array"
                assert checks["languagesCount"] > 0, "Should have at least one language"

                # Assert user agent and platform are set
                assert checks["userAgent"], "User agent should be set"
                assert checks["platform"], "Platform should be set"

                # For Chromium, check chrome object
                if "chromium" in client.browser_type.lower():
                    assert checks["hasChrome"], "Chrome object should exist for Chromium"

            finally:
                await session.close()


# === Helper Functions ===


@pytest.fixture
async def detection_client():
    """Fixture to create PhantomPersona client for detection tests.

    Yields:
        PhantomPersona client with BASIC protection level

    Example:
        >>> async def test_something(detection_client):
        ...     async with detection_client as client:
        ...         session = await client.new_session()
    """
    async with PhantomPersona(level=ProtectionLevel.BASIC) as client:
        yield client
