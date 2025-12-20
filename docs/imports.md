# Import Guide

This document shows all available imports from the `phantom-persona` library.

## Main Client

```python
from phantom_persona import PhantomPersona

# Create client with protection level
async with PhantomPersona(level=2) as client:
    session = await client.new_session()
    page = await session.new_page()
```

## Protection Levels

```python
from phantom_persona import ProtectionLevel

# Use enum for type safety
client = PhantomPersona(level=ProtectionLevel.MODERATE)

# Available levels
ProtectionLevel.NONE       # 0 - No protection
ProtectionLevel.BASIC      # 1 - Basic stealth
ProtectionLevel.MODERATE   # 2 - Moderate protection
ProtectionLevel.ADVANCED   # 3 - Advanced techniques
ProtectionLevel.STEALTH    # 4 - Maximum stealth
```

## Persona Management

```python
from phantom_persona import Persona, GeoInfo, DeviceInfo, Fingerprint

# Create custom persona
geo = GeoInfo(
    country="US",
    region="California",
    city="San Francisco",
    timezone="America/Los_Angeles",
    language="en-US"
)

device = DeviceInfo(
    platform="Win32",
    screen_width=1920,
    screen_height=1080,
    pixel_ratio=1.0
)

fingerprint = Fingerprint(
    user_agent="Mozilla/5.0...",
    device=device,
    webgl_vendor="Google Inc.",
    webgl_renderer="ANGLE..."
)

persona = Persona(
    fingerprint=fingerprint,
    geo=geo
)

# Use with client
session = await client.new_session(persona=persona)
```

## Proxy Configuration

```python
from phantom_persona.proxy import ProxyInfo

# From URL
proxy = ProxyInfo.from_url("http://user:pass@proxy.com:8080")

# From string
proxy = ProxyInfo.from_string("proxy.com:8080:user:pass")

# Manual creation
proxy = ProxyInfo(
    host="proxy.com",
    port=8080,
    protocol="http",
    username="user",
    password="pass"
)

# Use with session
session = await client.new_session(proxy=proxy)
```

## Configuration

```python
from phantom_persona.config import (
    PhantomConfig,
    BrowserConfig,
    ProxyConfig,
    FingerprintConfig,
    BehaviorConfig,
    RetryConfig,
    ConfigLoader
)

# Create config manually
config = PhantomConfig(
    level=2,
    browser=BrowserConfig(
        browser_type="chromium",
        headless=True
    ),
    proxy=ProxyConfig(
        enabled=True,
        validate_proxies=True
    )
)

# Load from file
config = ConfigLoader.load("config.yaml")

# Create from level
config = ConfigLoader.from_level(2)

# Use with client
client = PhantomPersona(config=config)
# or
client = PhantomPersona.from_config("config.yaml")
```

## Core Components

```python
from phantom_persona import (
    BrowserManager,
    ContextBuilder,
    ContextManager,
    Session
)

# Low-level browser management
manager = BrowserManager(browser_type="chromium")
await manager.start()
browser = manager.browser

# Context building
builder = ContextBuilder(browser)
builder.with_persona(persona).with_proxy(proxy)
context = await builder.build()

# Context management with plugins
context_mgr = ContextManager(browser, persona, plugins)
context = await context_mgr.create()

# Session usage
session = Session(context, persona)
page = await session.new_page()
await session.human_type(page, "#input", "text")
await session.human_click(page, "#button")
await session.close()
```

## Exceptions

```python
from phantom_persona import (
    PhantomException,        # Base exception
    BrowserException,        # Browser errors
    BrowserLaunchError,      # Launch failures
    BrowserContextError,     # Context errors
    ProxyException,          # Proxy errors
    ProxyValidationError,    # Proxy validation
    ProxyConnectionError,    # Proxy connection
    PersonaException,        # Persona errors
    PersonaNotFoundError,    # Persona not found
    PersonaExpiredError,     # Persona expired
    ConfigException,         # Config errors
    ConfigNotFoundError,     # Config not found
    ConfigValidationError,   # Config validation
    DetectionException,      # Detection errors
    SessionError             # Session errors
)

try:
    session = await client.new_session()
except BrowserLaunchError:
    print("Failed to launch browser")
except ProxyConnectionError:
    print("Proxy connection failed")
except PhantomException as e:
    print(f"General error: {e.message}")
    print(f"Details: {e.details}")
```

## Plugin System

```python
from phantom_persona import (
    Plugin,
    StealthPlugin,
    FingerprintPlugin,
    BehaviorPlugin,
    registry,
    register_plugin
)

# Get plugins for level
plugins = registry.get_for_level(level=2, browser_type="chromium")

# Create custom plugin
@register_plugin
class MyPlugin(StealthPlugin):
    name = "custom.stealth"
    priority = 50

    async def apply(self, context):
        await context.add_init_script("...")

# Check loaded plugins
client = PhantomPersona(level=2)
await client.start()
print(client.plugins)  # ['stealth.basic', 'fingerprint.navigator', ...]
```

## Complete Example

```python
from phantom_persona import (
    PhantomPersona,
    ProtectionLevel,
    Persona,
    GeoInfo,
    DeviceInfo,
    Fingerprint
)
from phantom_persona.proxy import ProxyInfo
from phantom_persona.config import PhantomConfig

# Create custom config
config = PhantomConfig(level=ProtectionLevel.MODERATE)

# Create proxy
proxy = ProxyInfo.from_url("http://user:pass@proxy.com:8080")

# Create persona
persona = Persona(
    fingerprint=Fingerprint(
        user_agent="Mozilla/5.0...",
        device=DeviceInfo(platform="Win32", screen_width=1920, screen_height=1080)
    ),
    geo=GeoInfo(country="US", timezone="America/Los_Angeles", language="en-US")
)

# Use everything together
async def main():
    async with PhantomPersona(config=config) as client:
        # Create session with persona and proxy
        session = await client.new_session(persona=persona, proxy=proxy)

        # Create page and navigate
        page = await session.new_page()
        await page.goto("https://example.com")

        # Use human-like interactions
        await session.human_type(page, "#search", "query")
        await session.human_click(page, "#submit")
        await session.human_scroll(page, 500)

        # Close session
        await session.close()

# Run
import asyncio
asyncio.run(main())
```

## Import Patterns

### Recommended for Simple Usage

```python
from phantom_persona import PhantomPersona

async with PhantomPersona(level=2) as client:
    session = await client.new_session()
    page = await session.new_page()
    await page.goto("https://example.com")
```

### Recommended for Advanced Usage

```python
from phantom_persona import (
    PhantomPersona,
    ProtectionLevel,
    Persona,
    GeoInfo,
    DeviceInfo,
    Fingerprint,
)
from phantom_persona.proxy import ProxyInfo
from phantom_persona.config import PhantomConfig, ConfigLoader

# Full control over configuration
config = PhantomConfig(
    level=ProtectionLevel.ADVANCED,
    browser=BrowserConfig(headless=False),
    behavior=BehaviorConfig(human_delays=True)
)

async with PhantomPersona(config=config) as client:
    # Custom persona and proxy
    session = await client.new_session(persona=my_persona, proxy=my_proxy)
```

### Recommended for Library Developers

```python
from phantom_persona import (
    Plugin,
    StealthPlugin,
    FingerprintPlugin,
    BehaviorPlugin,
    register_plugin,
    registry,
)
from phantom_persona.core import (
    BrowserManager,
    ContextBuilder,
    ContextManager,
    Session,
)

# Create custom plugins and use low-level APIs
```
