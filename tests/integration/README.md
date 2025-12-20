# Integration Tests

Integration tests for phantom-persona library that test browser automation and Playwright integration.

## Requirements

Integration tests require Playwright browsers to be installed. Install them with:

```bash
# Install Playwright browsers
playwright install chromium firefox webkit

# Or install with system dependencies
playwright install --with-deps chromium firefox webkit
```

## Running Tests

Run all integration tests:

```bash
pytest tests/integration/ -v
```

Run specific test file:

```bash
pytest tests/integration/test_browser.py -v
```

Run specific test:

```bash
pytest tests/integration/test_browser.py::test_browser_manager_start_close -v
```

## Test Coverage

### Browser Management (`test_browser.py`)

Tests for BrowserManager and browser context creation:

1. **test_browser_manager_start_close** - Browser lifecycle (start/close)
2. **test_browser_manager_context_manager** - Async context manager pattern
3. **test_browser_creates_context** - Browser context creation
4. **test_context_with_viewport** - Viewport configuration
5. **test_context_with_user_agent** - User agent customization
6. **test_context_with_locale** - Locale and timezone settings

Additional tests:
- Multiple browser instances
- Different browser types (Chromium, Firefox, WebKit)
- Invalid browser types
- Error handling
- Context isolation
- Permissions and geolocation
- Custom browser arguments

## Environment

Tests are marked with `@pytest.mark.asyncio` for async testing support.

Browser tests run in headless mode by default for CI/CD compatibility.

## Troubleshooting

### Browsers not installed

If you see errors about missing browsers:

```
Executable doesn't exist at /path/to/playwright/chromium
```

Run `playwright install` to download browsers.

### Network restrictions

If browser downloads fail with 403 errors, you may be behind a firewall or proxy. Configure environment variables:

```bash
export PLAYWRIGHT_DOWNLOAD_HOST=https://your-mirror.com
```

Or use pre-installed browsers in your environment.

### Headless mode issues

Some tests may require display for full functionality. Run in headed mode:

```python
config = BrowserConfig(headless=False)
```

## CI/CD

For CI/CD pipelines, ensure browsers are cached or installed as part of the pipeline:

```yaml
# GitHub Actions example
- name: Install Playwright browsers
  run: playwright install --with-deps chromium
```

## Notes

- Tests use real browser instances and may be slower than unit tests
- Each test creates and destroys browser instances for isolation
- Context managers ensure proper cleanup even if tests fail
- Tests are compatible with pytest-xdist for parallel execution
