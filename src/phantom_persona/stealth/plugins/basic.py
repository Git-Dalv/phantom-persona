"""Basic stealth plugin for Level 1 protection.

This plugin provides fundamental anti-detection techniques to hide
automation indicators and pass basic bot detection systems.
"""

from typing import TYPE_CHECKING

from phantom_persona.plugins import StealthPlugin, register_plugin

if TYPE_CHECKING:
    from playwright.async_api import BrowserContext


@register_plugin
class BasicStealthPlugin(StealthPlugin):
    """Basic stealth techniques to hide automation.

    Implements fundamental anti-detection measures:
    - Hides navigator.webdriver flag
    - Mocks navigator.plugins with realistic Chrome plugins
    - Sets navigator.languages from persona
    - Adds window.chrome object
    - Patches Permissions.query API

    This plugin is suitable for bypassing simple bot detection
    and is included in protection Level 1 and above.

    Example:
        >>> plugin = BasicStealthPlugin()
        >>> await plugin.apply(context)
    """

    name = "stealth.basic"
    priority = 10  # Apply early

    async def apply(self, context: "BrowserContext") -> None:
        """Apply basic stealth techniques to browser context.

        Injects JavaScript code before page load to hide automation
        indicators and make the browser appear more human-like.

        Args:
            context: Playwright browser context
        """
        # Apply all stealth patches
        await context.add_init_script(self._get_webdriver_patch())
        await context.add_init_script(self._get_plugins_patch())
        await context.add_init_script(self._get_languages_patch())
        await context.add_init_script(self._get_chrome_patch())
        await context.add_init_script(self._get_permissions_patch())

    def _get_webdriver_patch(self) -> str:
        """Get JavaScript code to hide navigator.webdriver.

        Returns:
            JavaScript code to patch webdriver property
        """
        return """
        // Patch navigator.webdriver
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
            configurable: true
        });

        // Also patch in prototype
        delete Object.getPrototypeOf(navigator).webdriver;
        """

    def _get_plugins_patch(self) -> str:
        """Get JavaScript code to mock navigator.plugins.

        Creates realistic Chrome plugin array with common plugins.

        Returns:
            JavaScript code to patch plugins
        """
        return """
        // Mock navigator.plugins with realistic Chrome plugins
        const plugins = [
            {
                0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format"},
                description: "Portable Document Format",
                filename: "internal-pdf-viewer",
                length: 1,
                name: "Chrome PDF Plugin"
            },
            {
                0: {type: "application/pdf", suffixes: "pdf", description: "Portable Document Format"},
                description: "Portable Document Format",
                filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
                length: 1,
                name: "Chrome PDF Viewer"
            },
            {
                0: {type: "application/x-nacl", suffixes: "", description: "Native Client Executable"},
                1: {type: "application/x-pnacl", suffixes: "", description: "Portable Native Client Executable"},
                description: "",
                filename: "internal-nacl-plugin",
                length: 2,
                name: "Native Client"
            }
        ];

        Object.defineProperty(navigator, 'plugins', {
            get: () => plugins,
            configurable: true
        });

        // Mock navigator.mimeTypes to match plugins
        const mimeTypes = [
            {type: "application/pdf", suffixes: "pdf", description: "Portable Document Format"},
            {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format"},
            {type: "application/x-nacl", suffixes: "", description: "Native Client Executable"},
            {type: "application/x-pnacl", suffixes: "", description: "Portable Native Client Executable"}
        ];

        Object.defineProperty(navigator, 'mimeTypes', {
            get: () => mimeTypes,
            configurable: true
        });
        """

    def _get_languages_patch(self) -> str:
        """Get JavaScript code to set navigator.languages.

        Sets realistic language preferences. In a full implementation,
        this would use values from the persona.

        Returns:
            JavaScript code to patch languages
        """
        return """
        // Set navigator.languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en'],
            configurable: true
        });

        Object.defineProperty(navigator, 'language', {
            get: () => 'en-US',
            configurable: true
        });
        """

    def _get_chrome_patch(self) -> str:
        """Get JavaScript code to add window.chrome object.

        Chrome browsers have a window.chrome object with specific properties.
        This patch adds a realistic chrome object.

        Returns:
            JavaScript code to patch window.chrome
        """
        return """
        // Add window.chrome object
        if (!window.chrome) {
            window.chrome = {
                runtime: {},
                loadTimes: function() {},
                csi: function() {},
                app: {}
            };
        }

        // Mock chrome.runtime
        if (window.chrome && !window.chrome.runtime) {
            Object.defineProperty(window.chrome, 'runtime', {
                value: {},
                writable: true,
                enumerable: true,
                configurable: true
            });
        }
        """

    def _get_permissions_patch(self) -> str:
        """Get JavaScript code to patch Permissions.query.

        Some bot detection systems check the Permissions API behavior.
        This patch makes it behave like a normal browser.

        Returns:
            JavaScript code to patch Permissions API
        """
        return """
        // Patch Permissions.query
        const originalQuery = navigator.permissions.query;

        navigator.permissions.query = (parameters) => {
            // For notifications, return denied to avoid permission prompts
            if (parameters.name === 'notifications') {
                return Promise.resolve({
                    state: 'denied',
                    onchange: null
                });
            }

            // For other permissions, use original behavior
            return originalQuery(parameters);
        };

        // Make the patch undetectable
        Object.defineProperty(navigator.permissions.query, 'toString', {
            value: () => 'function query() { [native code] }',
            configurable: true
        });
        """

    def is_compatible(self, browser_type: str) -> bool:
        """Check browser compatibility.

        This plugin is primarily designed for Chromium but has
        generic patches that work across browsers.

        Args:
            browser_type: Browser type ("chromium", "firefox", "webkit")

        Returns:
            True for all browser types
        """
        # Works with all browsers, though optimized for Chromium
        return True


__all__ = ["BasicStealthPlugin"]
