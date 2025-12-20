# End-to-End Tests

End-to-end tests for phantom-persona library that test anti-detection capabilities on real websites.

## Requirements

E2E tests require:

1. **Internet connection** - Tests access real websites
2. **Playwright browsers** - Install with:
   ```bash
   playwright install chromium firefox webkit
   ```
3. **Working network** - No firewall blocking detection sites

## Running Tests

Run all E2E tests:

```bash
pytest tests/e2e/ -v -m e2e
```

Run specific test:

```bash
pytest tests/e2e/test_detection.py::TestDetection::test_bot_sannysoft -v
```

Run only slow tests:

```bash
pytest tests/e2e/ -v -m "e2e and slow"
```

Skip slow tests:

```bash
pytest tests/e2e/ -v -m "e2e and not slow"
```

## Test Markers

Tests use pytest markers for organization:

- `@pytest.mark.e2e` - End-to-end tests
- `@pytest.mark.slow` - Tests that may take longer (>5 seconds)
- `@pytest.mark.asyncio` - Async tests requiring pytest-asyncio

## Test Coverage

### Detection Evasion (`test_detection.py`)

Tests anti-detection capabilities on real bot detection websites:

#### `test_bot_sannysoft`

Tests on https://bot.sannysoft.com

Verifies:
- ✓ `navigator.webdriver` is false/undefined
- ✓ `window.navigator.webdriver` is false/undefined
- ✓ Chrome object exists (for Chromium)
- ✓ Plugins are accessible
- ✓ Languages array is populated
- ✓ Permissions API exists
- ✓ No PhantomJS indicators (`window.callPhantom`)
- ✓ No Nightmare.js indicators (`window.__nightmare`)

#### `test_browserleaks_navigator`

Tests on https://browserleaks.com/javascript

Verifies:
- ✓ `navigator.webdriver` is false/undefined
- ✓ No automation framework indicators:
  - PhantomJS: `window.callPhantom`, `window._phantom`
  - Nightmare.js: `window.__nightmare`
  - Selenium: `window._selenium`
  - DOM automation: `window.domAutomation`
- ✓ Navigator properties are realistic:
  - userAgent, platform, language, languages
  - vendor, hardwareConcurrency, deviceMemory
  - plugins, maxTouchPoints
- ✓ Screen properties are realistic:
  - width, height, availWidth, availHeight
  - colorDepth (24/30/32), pixelDepth
- ✓ Date and Math objects are intact

#### `test_basic_stealth_features`

Sanity check test (doesn't require internet)

Verifies:
- ✓ All automation indicators are hidden
- ✓ Normal browser properties exist
- ✓ Chrome object exists for Chromium
- ✓ User agent and platform are set

## Configuration

Tests use `PhantomPersona` with `ProtectionLevel.BASIC`:

```python
async with PhantomPersona(level=ProtectionLevel.BASIC) as client:
    session = await client.new_session()
    page = await session.new_page()
    # Test anti-detection...
```

Higher protection levels can be tested by changing the level:

```python
# For maximum stealth
async with PhantomPersona(level=ProtectionLevel.STEALTH) as client:
    # ...
```

## Troubleshooting

### Tests fail with timeout

Detection sites may be slow or unreachable. Increase timeout:

```python
await page.goto(url, wait_until="networkidle", timeout=60000)  # 60 seconds
```

### Tests fail with detection

If tests fail because automation is detected:

1. **Update stealth plugins** - Detection sites evolve, plugins may need updates
2. **Increase protection level** - Try `ProtectionLevel.ADVANCED` or `STEALTH`
3. **Check Playwright version** - Update to latest Playwright
4. **Manual verification** - Capture screenshots to verify:
   ```python
   await page.screenshot(path="detection_result.png")
   ```

### Network errors

If tests fail with network errors:

- Check internet connection
- Verify detection sites are accessible
- Check firewall/proxy settings
- Try different browser type (Firefox, WebKit)

### Flaky tests

Detection tests may be flaky due to:

- Network latency
- Site changes (detection methods updated)
- Browser version differences

Use retries for flaky tests:

```bash
pytest tests/e2e/ --maxfail=1 --reruns=2
```

## CI/CD Integration

For CI/CD pipelines:

```yaml
# GitHub Actions example
- name: Install Playwright browsers
  run: playwright install --with-deps chromium

- name: Run E2E tests
  run: pytest tests/e2e/ -v -m e2e
  timeout-minutes: 10
```

**Note:** E2E tests may be unstable in CI due to network conditions. Consider:

- Running only on specific branches (main, staging)
- Using retry strategies
- Allowing failures for flaky tests
- Caching screenshots for debugging

## Best Practices

1. **Run locally first** - Verify tests pass before CI
2. **Check detection sites manually** - Understand what's being tested
3. **Update regularly** - Detection methods evolve
4. **Screenshot on failure** - Capture evidence for debugging
5. **Monitor execution time** - Flag slow tests with `@pytest.mark.slow`
6. **Use realistic delays** - Don't rush through tests, act human-like

## Expected Results

When anti-detection works correctly:

- ✅ All webdriver checks should pass (false/undefined)
- ✅ No automation framework indicators
- ✅ Navigator properties look like real browser
- ✅ Screen and hardware properties are realistic
- ✅ No suspicious JavaScript modifications

When detection fails:

- ❌ `navigator.webdriver` is true
- ❌ Automation indicators present
- ❌ Missing or suspicious browser properties
- ❌ Obvious JavaScript tampering

## Websites Tested

Current detection sites:

1. **bot.sannysoft.com** - Comprehensive bot detection tests
2. **browserleaks.com/javascript** - JavaScript environment analysis

Additional sites that can be added:

- arh.antoinevastel.com/bots/areyouheadless
- pixelscan.net
- browserscan.net
- deviceandbrowserinfo.com/are_you_a_bot

## Notes

- Tests use headless mode by default for speed
- Detection sites may block automated access
- Tests require maintenance as detection evolves
- Some checks may be browser-specific (Chromium vs Firefox)
- Geographic restrictions may affect some sites
