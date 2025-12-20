# Phantom Persona

**Browser automation with anti-detection** — Playwright-based library for web scraping and automation with built-in bot detection evasion.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- 🎭 **Multiple protection levels** (0-4) - from basic to stealth
- 🌐 **Persona management** - unique browser fingerprints and identities
- 🔐 **Proxy support** - HTTP, HTTPS, SOCKS5 with authentication
- 🤖 **Human-like behavior** - typing, clicking, scrolling simulation
- 🔌 **Plugin system** - extensible stealth techniques
- ⚡ **Async/await** - built on Playwright's async API
- 📝 **Type hints** - full Python 3.9+ type annotations

## Installation

```bash
# Install the library
pip install phantom-persona

# Install Playwright browsers
playwright install chromium firefox webkit
```

## Quick Start

### 1. Simplest Usage

```python
import asyncio
from phantom_persona import PhantomPersona, ProtectionLevel

async def main():
    async with PhantomPersona(level=ProtectionLevel.BASIC) as phantom:
        # Quick page creation
        page = await phantom.new_page()
        await page.goto("https://example.com")

        title = await page.title()
        print(f"Title: {title}")

asyncio.run(main())
```

### 2. Using Sessions

```python
async def main():
    async with PhantomPersona(level=ProtectionLevel.MODERATE) as phantom:
        # Create session with persona
        session = await phantom.new_session()

        try:
            page = await session.new_page()
            await page.goto("https://example.com")

            # Human-like behavior
            await session.human_delay()
            await session.human_type(page, "#search", "query")
            await session.human_click(page, "#submit")
        finally:
            await session.close()
```

### 3. Using Configuration

```python
from phantom_persona import PhantomPersona, Persona, GeoInfo, DeviceInfo, Fingerprint
from phantom_persona.proxy import ProxyInfo
from datetime import datetime

async def main():
    # Custom persona
    geo = GeoInfo(
        country_code="US",
        country="United States",
        city="New York",
        timezone="America/New_York",
        language="en-US",
        languages=["en-US", "en"]
    )

    device = DeviceInfo(
        type="desktop",
        platform="Win32",
        vendor="Google Inc.",
        renderer="ANGLE (Intel)",
        screen_width=1920,
        screen_height=1080
    )

    fingerprint = Fingerprint(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
        device=device
    )

    persona = Persona(
        fingerprint=fingerprint,
        geo=geo,
        created_at=datetime.now()
    )

    # Proxy
    proxy = ProxyInfo.from_url("http://user:pass@proxy.com:8080")

    # Use custom persona and proxy
    async with PhantomPersona(level=ProtectionLevel.ADVANCED) as phantom:
        session = await phantom.new_session(persona=persona, proxy=proxy)
        # ... your code here
        await session.close()
```

## Protection Levels

| Level | Name | Description | Use Case |
|-------|------|-------------|----------|
| 0 | NONE | No protection | Testing, trusted sites |
| 1 | BASIC | Basic stealth (webdriver hiding) | Simple scraping |
| 2 | MODERATE | Medium protection + navigator spoofing | General use |
| 3 | ADVANCED | Advanced techniques + canvas/webgl | Strict sites |
| 4 | STEALTH | Maximum stealth + all features | Maximum evasion |

## Configuration

Create `config.yaml`:

```yaml
level: 2

browser:
  type: chromium
  headless: true
  args:
    - --no-sandbox
    - --disable-dev-shm-usage

proxy:
  enabled: false
  validate_proxies: true
  rotation: per_session

fingerprint:
  consistency: auto
  device_type: desktop

behavior:
  human_delays: true
  delay_range: [0.3, 1.5]

retry:
  enabled: true
  max_attempts: 3
  backoff: exponential
```

Load configuration:

```python
from phantom_persona import PhantomPersona
from phantom_persona.config import ConfigLoader

config = ConfigLoader.load("config.yaml")
async with PhantomPersona(config=config) as phantom:
    # ...
```

## Architecture

```
phantom-persona/
├── client.py              # Main entry point (PhantomPersona)
├── config/                # Configuration management
│   ├── schema.py         # Pydantic models
│   ├── loader.py         # YAML/JSON loading
│   └── levels.py         # Protection levels
├── core/                  # Core functionality
│   ├── browser.py        # Browser management
│   ├── context.py        # Context builder
│   ├── session.py        # Session with human behavior
│   └── exceptions.py     # Custom exceptions
├── persona/               # Persona management
│   └── identity.py       # GeoInfo, DeviceInfo, Fingerprint
├── proxy/                 # Proxy handling
│   └── models.py         # ProxyInfo
└── plugins/               # Anti-detection plugins
    ├── base.py           # Plugin ABC
    ├── registry.py       # Plugin registry
    └── stealth/          # Stealth plugins
        └── basic.py      # Basic stealth (webdriver hiding)
```

### Plugin System

```python
from phantom_persona.plugins import register_plugin, StealthPlugin

@register_plugin
class MyStealthPlugin(StealthPlugin):
    name = "stealth.custom"
    priority = 50

    async def apply(self, context):
        # Inject JavaScript to hide automation
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
```

## Development

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run unit tests
pytest tests/unit/ -v

# Run integration tests (requires browsers)
pytest tests/integration/ -v

# Run E2E tests (requires internet)
pytest tests/e2e/ -v -m e2e

# Run all tests
pytest -v

# With coverage
pytest --cov=phantom_persona --cov-report=html
```

### Test Markers

```bash
# Only unit tests
pytest -m unit

# Only slow tests
pytest -m slow

# Skip slow tests
pytest -m "not slow"

# Only E2E tests
pytest -m e2e
```

## Roadmap

### ✅ Phase 1: Core Functionality (Current)
- [x] Browser management (Chromium, Firefox, WebKit)
- [x] Basic stealth plugins
- [x] Persona system
- [x] Proxy support
- [x] Session management
- [x] Human-like behavior
- [x] Configuration system
- [x] Plugin architecture

### 🚧 Phase 2: Advanced Features (Next)
- [ ] Fingerprint randomization
- [ ] Canvas/WebGL noise
- [ ] Audio fingerprint spoofing
- [ ] Advanced navigator properties
- [ ] Plugin marketplace
- [ ] Persona persistence
- [ ] Browser profile management

### 📋 Phase 3: Ecosystem
- [ ] CLI tool
- [ ] Web dashboard
- [ ] Proxy rotation strategies
- [ ] Captcha integration
- [ ] Cloud browser support
- [ ] Docker images
- [ ] Kubernetes deployment

### 🎯 Phase 4: Enterprise
- [ ] Distributed scraping
- [ ] Request queues
- [ ] Rate limiting
- [ ] Monitoring & analytics
- [ ] Team collaboration
- [ ] API service
- [ ] Commercial support

## License

MIT License

```
Copyright (c) 2024 Phantom Persona Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Disclaimer

This library is designed for legitimate web scraping and automation tasks. Users are responsible for complying with websites' Terms of Service and applicable laws. The authors assume no liability for misuse.

---

**Made with ❤️ for the web automation community**
