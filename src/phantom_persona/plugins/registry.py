"""Plugin registry and auto-discovery system.

This module provides a centralized registry for managing plugins,
including automatic discovery and instantiation based on protection levels.
"""

import importlib
from typing import TYPE_CHECKING, Dict, List, Optional, Type, Union

from phantom_persona.config.levels import LEVEL_PLUGINS, ProtectionLevel

if TYPE_CHECKING:
    from phantom_persona.plugins.base import Plugin


class PluginRegistry:
    """Centralized registry for managing plugins.

    Implements singleton pattern to ensure a single registry instance
    throughout the application. Provides plugin registration, discovery,
    and instantiation based on protection levels.

    Example:
        >>> from phantom_persona.plugins.registry import registry
        >>> from phantom_persona import StealthPlugin
        >>>
        >>> class MyPlugin(StealthPlugin):
        ...     name = "stealth.custom"
        ...     async def apply(self, context):
        ...         pass
        >>>
        >>> registry.register(MyPlugin)
        >>> plugins = registry.get_for_level(ProtectionLevel.BASIC)
    """

    _instance: Optional["PluginRegistry"] = None

    def __new__(cls) -> "PluginRegistry":
        """Create or return singleton instance.

        Implements singleton pattern to ensure only one registry exists.

        Returns:
            The singleton PluginRegistry instance
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._plugins: Dict[str, Type["Plugin"]] = {}
        return cls._instance

    def register(self, plugin_class: Type["Plugin"]) -> Type["Plugin"]:
        """Register a plugin class in the registry.

        Can be used as a decorator or called directly.
        Stores the plugin class by its name attribute.

        Args:
            plugin_class: Plugin class to register (must have 'name' attribute)

        Returns:
            The same plugin class (for decorator usage)

        Raises:
            AttributeError: If plugin_class doesn't have 'name' attribute

        Example:
            >>> # As a decorator
            >>> @registry.register
            ... class MyPlugin(StealthPlugin):
            ...     name = "stealth.myplugin"
            ...     async def apply(self, context):
            ...         pass
            >>>
            >>> # Direct call
            >>> registry.register(MyPlugin)
        """
        if not hasattr(plugin_class, "name"):
            raise AttributeError(
                f"Plugin class {plugin_class.__name__} must have a 'name' attribute"
            )

        self._plugins[plugin_class.name] = plugin_class
        return plugin_class

    def get(self, name: str) -> Type["Plugin"]:
        """Get plugin class by name.

        Args:
            name: Plugin name (e.g., "stealth.basic", "fingerprint.canvas")

        Returns:
            Plugin class

        Raises:
            KeyError: If plugin with given name is not registered

        Example:
            >>> plugin_class = registry.get("stealth.basic")
            >>> plugin = plugin_class()
            >>> await plugin.apply(context)
        """
        if name not in self._plugins:
            raise KeyError(
                f"Plugin '{name}' not found in registry. "
                f"Available plugins: {', '.join(self.list_all())}"
            )
        return self._plugins[name]

    def get_for_level(
        self, level: Union[ProtectionLevel, int], browser_type: str = "chromium"
    ) -> List["Plugin"]:
        """Get instantiated plugins for a protection level.

        Retrieves all plugins defined for the given protection level,
        instantiates them, filters by browser compatibility, and sorts
        by priority.

        Args:
            level: Protection level (ProtectionLevel enum or int 0-4)
            browser_type: Browser type for compatibility check (default: "chromium")

        Returns:
            List of instantiated plugin objects, sorted by priority

        Example:
            >>> plugins = registry.get_for_level(ProtectionLevel.MODERATE)
            >>> for plugin in plugins:
            ...     await plugin.apply(context)
            >>>
            >>> # With browser filter
            >>> firefox_plugins = registry.get_for_level(2, browser_type="firefox")
        """
        # Convert int to ProtectionLevel if needed
        if isinstance(level, int):
            level = ProtectionLevel(level)

        plugin_names = LEVEL_PLUGINS.get(level, [])
        plugins: List["Plugin"] = []

        for name in plugin_names:
            try:
                plugin_class = self.get(name)
                plugin = plugin_class()

                # Only include if compatible with browser
                if plugin.is_compatible(browser_type):
                    plugins.append(plugin)
            except KeyError:
                # Plugin not registered yet, skip it
                # This can happen during initial setup or if a plugin module
                # hasn't been imported yet
                pass

        # Sort by priority (lower values first)
        return sorted(plugins, key=lambda p: p.priority)

    def list_all(self) -> List[str]:
        """List all registered plugin names.

        Returns:
            Sorted list of plugin names

        Example:
            >>> all_plugins = registry.list_all()
            >>> print(all_plugins)
            ['behavior.delays', 'fingerprint.canvas', 'stealth.basic', ...]
        """
        return sorted(self._plugins.keys())

    def autodiscover(self) -> None:
        """Automatically discover and import plugins from standard modules.

        Attempts to import predefined plugin modules to trigger their
        registration. This is typically called once during library initialization.

        Silently ignores ImportError if modules don't exist yet.

        Example:
            >>> registry.autodiscover()
            >>> # All standard plugins are now registered
            >>> print(registry.list_all())
        """
        modules = [
            "phantom_persona.stealth.plugins",
            "phantom_persona.fingerprint.plugins",
            "phantom_persona.behavior",
        ]

        for module_name in modules:
            try:
                importlib.import_module(module_name)
            except ImportError:
                # Module doesn't exist yet or has import errors
                # This is expected during development or if optional
                # plugin modules aren't installed
                pass

    def clear(self) -> None:
        """Clear all registered plugins.

        Primarily used for testing. Removes all plugins from the registry.

        Example:
            >>> registry.clear()
            >>> registry.list_all()
            []
        """
        self._plugins.clear()

    def __contains__(self, name: str) -> bool:
        """Check if plugin is registered.

        Args:
            name: Plugin name to check

        Returns:
            True if plugin is registered, False otherwise

        Example:
            >>> "stealth.basic" in registry
            True
            >>> "nonexistent.plugin" in registry
            False
        """
        return name in self._plugins

    def __len__(self) -> int:
        """Get number of registered plugins.

        Returns:
            Number of registered plugins

        Example:
            >>> len(registry)
            12
        """
        return len(self._plugins)

    def __repr__(self) -> str:
        """String representation of registry.

        Returns:
            String showing number of registered plugins

        Example:
            >>> repr(registry)
            '<PluginRegistry: 12 plugins registered>'
        """
        return f"<PluginRegistry: {len(self._plugins)} plugins registered>"


# Global registry instance (singleton)
registry = PluginRegistry()


def register_plugin(cls: Type["Plugin"]) -> Type["Plugin"]:
    """Decorator for convenient plugin registration.

    Convenience function that registers a plugin class in the global registry.
    Can be used as a class decorator.

    Args:
        cls: Plugin class to register

    Returns:
        The same plugin class

    Example:
        >>> from phantom_persona.plugins import register_plugin, StealthPlugin
        >>>
        >>> @register_plugin
        ... class CustomStealthPlugin(StealthPlugin):
        ...     name = "stealth.custom"
        ...     priority = 15
        ...
        ...     async def apply(self, context):
        ...         await context.add_init_script("console.log('Custom stealth')")
    """
    return registry.register(cls)


__all__ = [
    "PluginRegistry",
    "registry",
    "register_plugin",
]
