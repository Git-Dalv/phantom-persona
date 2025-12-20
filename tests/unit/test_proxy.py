"""Unit tests for proxy module.

Tests for ProxyInfo dataclass and its methods.
"""

from datetime import datetime

import pytest

from phantom_persona.proxy import ProxyInfo


# === Fixtures ===


@pytest.fixture
def simple_proxy():
    """Simple proxy without authentication.

    Returns:
        ProxyInfo instance without auth
    """
    return ProxyInfo(host="proxy.example.com", port=8080)


@pytest.fixture
def auth_proxy():
    """Proxy with authentication.

    Returns:
        ProxyInfo instance with username and password
    """
    return ProxyInfo(
        host="proxy.example.com",
        port=8080,
        username="testuser",
        password="testpass",
    )


# === Creation Tests ===


def test_proxy_creation():
    """Test basic ProxyInfo creation.

    Verifies:
    - Proxy can be created with host and port
    - Default protocol is 'http'
    - Default values are set correctly
    - Optional fields are None or have proper defaults
    """
    proxy = ProxyInfo(host="proxy.example.com", port=8080)

    # Check required fields
    assert proxy.host == "proxy.example.com"
    assert proxy.port == 8080

    # Check defaults
    assert proxy.protocol == "http"
    assert proxy.username is None
    assert proxy.password is None
    assert proxy.geo is None
    assert proxy.speed_ms is None
    assert proxy.is_residential is False
    assert proxy.is_valid is True
    assert proxy.last_check is None
    assert proxy.fail_count == 0


def test_proxy_creation_with_auth():
    """Test proxy creation with authentication.

    Verifies:
    - Username and password can be set
    - All fields are stored correctly
    """
    proxy = ProxyInfo(
        host="proxy.example.com",
        port=8080,
        username="user123",
        password="pass456",
    )

    assert proxy.username == "user123"
    assert proxy.password == "pass456"


def test_proxy_creation_with_protocol():
    """Test proxy creation with different protocols.

    Verifies:
    - Protocol can be http, https, or socks5
    """
    for protocol in ["http", "https", "socks5"]:
        proxy = ProxyInfo(host="proxy.com", port=8080, protocol=protocol)
        assert proxy.protocol == protocol


# === URL Property Tests ===


def test_proxy_url_property(simple_proxy):
    """Test URL property without authentication.

    Verifies:
    - URL is formatted as protocol://host:port
    - No authentication in URL
    """
    url = simple_proxy.url

    assert url == "http://proxy.example.com:8080"
    assert "@" not in url  # No auth


def test_proxy_url_with_auth(auth_proxy):
    """Test URL property with authentication.

    Verifies:
    - URL includes username:password@
    - Format is protocol://user:pass@host:port
    - Credentials are properly encoded
    """
    url = auth_proxy.url

    assert url == "http://testuser:testpass@proxy.example.com:8080"
    assert "testuser:testpass@" in url


def test_proxy_url_with_special_chars():
    """Test URL property with special characters in credentials.

    Verifies:
    - Special characters are URL-encoded
    - @ symbol in password is encoded
    """
    proxy = ProxyInfo(
        host="proxy.com",
        port=8080,
        username="user@example.com",
        password="p@ss:word!",
    )

    url = proxy.url

    # Check that special chars are encoded
    assert "user%40example.com" in url  # @ encoded as %40
    assert "p%40ss%3Aword%21" in url  # @:! encoded


def test_proxy_url_different_protocols():
    """Test URL property with different protocols.

    Verifies:
    - Protocol is included in URL
    """
    for protocol in ["http", "https", "socks5"]:
        proxy = ProxyInfo(host="proxy.com", port=8080, protocol=protocol)
        assert proxy.url.startswith(f"{protocol}://")


# === Playwright Proxy Tests ===


def test_proxy_playwright_format(simple_proxy):
    """Test playwright_proxy property format.

    Verifies:
    - Returns dict with 'server' key
    - Server format is protocol://host:port
    - No username/password keys when not authenticated
    """
    playwright_config = simple_proxy.playwright_proxy

    assert isinstance(playwright_config, dict)
    assert "server" in playwright_config
    assert playwright_config["server"] == "http://proxy.example.com:8080"
    assert "username" not in playwright_config
    assert "password" not in playwright_config


def test_proxy_playwright_format_with_auth(auth_proxy):
    """Test playwright_proxy property with authentication.

    Verifies:
    - Returns dict with server, username, password
    - Server does not include auth (separate keys)
    - Username and password are in separate fields
    """
    playwright_config = auth_proxy.playwright_proxy

    assert isinstance(playwright_config, dict)
    assert "server" in playwright_config
    assert "username" in playwright_config
    assert "password" in playwright_config

    # Server should not contain auth
    assert "@" not in playwright_config["server"]
    assert playwright_config["server"] == "http://proxy.example.com:8080"

    # Credentials in separate fields
    assert playwright_config["username"] == "testuser"
    assert playwright_config["password"] == "testpass"


def test_proxy_playwright_format_protocols():
    """Test playwright_proxy with different protocols.

    Verifies:
    - Protocol is included in server URL
    """
    for protocol in ["http", "https", "socks5"]:
        proxy = ProxyInfo(host="proxy.com", port=8080, protocol=protocol)
        config = proxy.playwright_proxy
        assert config["server"].startswith(f"{protocol}://")


# === from_url Tests ===


def test_proxy_from_url():
    """Test parsing proxy from URL format.

    Verifies:
    - from_url() parses protocol://user:pass@host:port
    - All components are extracted correctly
    """
    proxy = ProxyInfo.from_url("http://user:pass@proxy.example.com:8080")

    assert proxy.host == "proxy.example.com"
    assert proxy.port == 8080
    assert proxy.protocol == "http"
    assert proxy.username == "user"
    assert proxy.password == "pass"


def test_proxy_from_url_without_auth():
    """Test parsing proxy URL without authentication.

    Verifies:
    - URL without auth is parsed correctly
    - Username and password are None
    """
    proxy = ProxyInfo.from_url("http://proxy.example.com:8080")

    assert proxy.host == "proxy.example.com"
    assert proxy.port == 8080
    assert proxy.username is None
    assert proxy.password is None


def test_proxy_from_url_https():
    """Test parsing HTTPS proxy URL.

    Verifies:
    - HTTPS protocol is recognized
    """
    proxy = ProxyInfo.from_url("https://proxy.example.com:443")

    assert proxy.protocol == "https"
    assert proxy.port == 443


def test_proxy_from_url_socks5():
    """Test parsing SOCKS5 proxy URL.

    Verifies:
    - SOCKS5 protocol is recognized
    """
    proxy = ProxyInfo.from_url("socks5://user:pass@proxy.example.com:1080")

    assert proxy.protocol == "socks5"
    assert proxy.port == 1080
    assert proxy.username == "user"


def test_proxy_from_url_invalid_no_host():
    """Test from_url with missing hostname.

    Verifies:
    - Raises ValueError for invalid URL
    """
    with pytest.raises(ValueError, match="missing hostname"):
        ProxyInfo.from_url("http://:8080")


def test_proxy_from_url_invalid_no_port():
    """Test from_url with missing port.

    Verifies:
    - Raises ValueError for missing port
    """
    with pytest.raises(ValueError, match="missing port"):
        ProxyInfo.from_url("http://proxy.example.com")


def test_proxy_from_url_invalid_protocol():
    """Test from_url with invalid protocol.

    Verifies:
    - Raises ValueError for unsupported protocol
    """
    with pytest.raises(ValueError, match="Invalid protocol"):
        ProxyInfo.from_url("ftp://proxy.example.com:8080")


# === from_string Tests ===


def test_proxy_from_string_simple():
    """Test parsing proxy from simple string format.

    Verifies:
    - from_string() parses "host:port" format
    - No authentication is set
    - Default protocol is http
    """
    proxy = ProxyInfo.from_string("proxy.example.com:8080")

    assert proxy.host == "proxy.example.com"
    assert proxy.port == 8080
    assert proxy.protocol == "http"  # default
    assert proxy.username is None
    assert proxy.password is None


def test_proxy_from_string_with_auth():
    """Test parsing proxy from string with authentication.

    Verifies:
    - from_string() parses "host:port:username:password" format
    - All components are extracted correctly
    """
    proxy = ProxyInfo.from_string("proxy.example.com:8080:user:pass")

    assert proxy.host == "proxy.example.com"
    assert proxy.port == 8080
    assert proxy.username == "user"
    assert proxy.password == "pass"


def test_proxy_from_string_url_format():
    """Test from_string delegates to from_url for URL format.

    Verifies:
    - Strings with :// are treated as URLs
    - from_url is called internally
    """
    proxy = ProxyInfo.from_string("http://user:pass@proxy.example.com:8080")

    assert proxy.host == "proxy.example.com"
    assert proxy.port == 8080
    assert proxy.protocol == "http"
    assert proxy.username == "user"
    assert proxy.password == "pass"


def test_proxy_from_string_invalid_format():
    """Test from_string with invalid format.

    Verifies:
    - Raises ValueError for invalid format
    - Only 2 or 4 parts are valid (host:port or host:port:user:pass)
    """
    with pytest.raises(ValueError, match="Invalid proxy string format"):
        ProxyInfo.from_string("proxy.example.com:8080:user")  # 3 parts

    with pytest.raises(ValueError, match="Invalid proxy string format"):
        ProxyInfo.from_string("proxy.example.com")  # 1 part


def test_proxy_from_string_various_formats():
    """Test from_string with various valid formats.

    Verifies:
    - Multiple formats are supported
    - All parse correctly
    """
    # Simple format
    p1 = ProxyInfo.from_string("proxy1.com:8080")
    assert p1.host == "proxy1.com" and p1.port == 8080

    # With auth
    p2 = ProxyInfo.from_string("proxy2.com:8080:admin:secret")
    assert p2.username == "admin" and p2.password == "secret"

    # URL format
    p3 = ProxyInfo.from_string("https://proxy3.com:443")
    assert p3.protocol == "https" and p3.port == 443


# === Status Tracking Tests ===


def test_proxy_mark_failed(simple_proxy):
    """Test mark_failed() increments fail_count.

    Verifies:
    - fail_count is incremented
    - last_check is updated
    - is_valid remains True initially
    """
    assert simple_proxy.fail_count == 0
    assert simple_proxy.is_valid is True

    # Mark as failed once
    before = datetime.now()
    simple_proxy.mark_failed()
    after = datetime.now()

    assert simple_proxy.fail_count == 1
    assert simple_proxy.is_valid is True  # Still valid after 1 failure
    assert simple_proxy.last_check is not None
    assert before <= simple_proxy.last_check <= after


def test_proxy_mark_failed_multiple_times():
    """Test multiple consecutive failures.

    Verifies:
    - fail_count increases with each call
    - Each call updates last_check
    """
    proxy = ProxyInfo(host="proxy.com", port=8080)

    for i in range(1, 4):
        proxy.mark_failed()
        assert proxy.fail_count == i
        assert proxy.last_check is not None


def test_proxy_invalid_after_failures():
    """Test proxy becomes invalid after 3+ failures.

    Verifies:
    - is_valid becomes False after fail_count > 3
    - Threshold is 3 failures
    """
    proxy = ProxyInfo(host="proxy.com", port=8080)

    # First 3 failures - still valid
    for _ in range(3):
        proxy.mark_failed()
        assert proxy.is_valid is True

    # 4th failure - becomes invalid
    proxy.mark_failed()
    assert proxy.fail_count == 4
    assert proxy.is_valid is False


def test_proxy_mark_valid(simple_proxy):
    """Test mark_valid() updates proxy status.

    Verifies:
    - is_valid is set to True
    - fail_count is reset to 0
    - speed_ms is updated
    - last_check is updated
    """
    # Simulate some failures first
    simple_proxy.fail_count = 5
    simple_proxy.is_valid = False

    # Mark as valid
    before = datetime.now()
    simple_proxy.mark_valid(speed_ms=150)
    after = datetime.now()

    assert simple_proxy.is_valid is True
    assert simple_proxy.fail_count == 0
    assert simple_proxy.speed_ms == 150
    assert simple_proxy.last_check is not None
    assert before <= simple_proxy.last_check <= after


def test_proxy_mark_valid_recovery():
    """Test proxy recovery from invalid state.

    Verifies:
    - Proxy can recover from invalid state
    - All counters are properly reset
    """
    proxy = ProxyInfo(host="proxy.com", port=8080)

    # Make it invalid
    for _ in range(5):
        proxy.mark_failed()
    assert proxy.is_valid is False
    assert proxy.fail_count == 5

    # Recover
    proxy.mark_valid(speed_ms=200)

    assert proxy.is_valid is True
    assert proxy.fail_count == 0
    assert proxy.speed_ms == 200


# === Edge Cases ===


def test_proxy_port_types():
    """Test proxy creation with different port numbers.

    Verifies:
    - Common ports work correctly
    """
    common_ports = [80, 443, 1080, 3128, 8080, 8888]

    for port in common_ports:
        proxy = ProxyInfo(host="proxy.com", port=port)
        assert proxy.port == port


def test_proxy_residential_flag():
    """Test is_residential flag.

    Verifies:
    - Flag defaults to False
    - Can be set to True
    """
    proxy = ProxyInfo(host="proxy.com", port=8080)
    assert proxy.is_residential is False

    proxy_residential = ProxyInfo(host="proxy.com", port=8080, is_residential=True)
    assert proxy_residential.is_residential is True


def test_proxy_with_geo_info():
    """Test proxy with geographical information.

    Verifies:
    - GeoInfo can be attached to proxy
    """
    from phantom_persona.persona import GeoInfo

    geo = GeoInfo(
        country_code="US",
        country="United States",
        city="New York",
        timezone="America/New_York",
        language="en-US",
        languages=["en-US", "en"],
    )

    proxy = ProxyInfo(host="us-proxy.com", port=8080, geo=geo)

    assert proxy.geo is not None
    assert proxy.geo.country == "United States"
    assert proxy.geo.city == "New York"


def test_proxy_speed_tracking():
    """Test speed tracking across multiple checks.

    Verifies:
    - speed_ms can be updated multiple times
    - Latest value is preserved
    """
    proxy = ProxyInfo(host="proxy.com", port=8080)

    assert proxy.speed_ms is None

    # First check - fast
    proxy.mark_valid(speed_ms=100)
    assert proxy.speed_ms == 100

    # Second check - slower
    proxy.mark_valid(speed_ms=250)
    assert proxy.speed_ms == 250


# === Integration Tests ===


def test_proxy_complete_lifecycle():
    """Test complete proxy lifecycle.

    Verifies:
    - Create, validate, fail, recover workflow
    """
    # Create from string
    proxy = ProxyInfo.from_string("proxy.example.com:8080:user:pass")

    # Initial state
    assert proxy.is_valid is True
    assert proxy.fail_count == 0

    # First successful check
    proxy.mark_valid(speed_ms=120)
    assert proxy.speed_ms == 120
    assert proxy.fail_count == 0

    # Some failures
    proxy.mark_failed()
    proxy.mark_failed()
    assert proxy.fail_count == 2
    assert proxy.is_valid is True  # Still valid

    # Recovery
    proxy.mark_valid(speed_ms=150)
    assert proxy.fail_count == 0
    assert proxy.is_valid is True

    # Check URL generation
    url = proxy.url
    assert "user:pass@" in url
    assert "proxy.example.com:8080" in url

    # Check Playwright format
    pw_config = proxy.playwright_proxy
    assert pw_config["username"] == "user"
    assert pw_config["password"] == "pass"


def test_proxy_format_conversions():
    """Test conversions between different formats.

    Verifies:
    - URL can be generated from parsed proxy
    - Roundtrip preserves data
    """
    original_url = "http://admin:secret@proxy.example.com:8080"

    # Parse from URL
    proxy = ProxyInfo.from_url(original_url)

    # Generate URL back
    generated_url = proxy.url

    # Should match
    assert generated_url == original_url

    # Parse from string format
    proxy2 = ProxyInfo.from_string("proxy2.com:8080:user:pass")

    # Generate URL
    url2 = proxy2.url
    assert url2 == "http://user:pass@proxy2.com:8080"
