"""Proxy configuration models.

This module defines data structures for proxy configuration and management,
including validation, status tracking, and format conversions.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Literal, Optional
from urllib.parse import quote, urlparse

from phantom_persona.persona.identity import GeoInfo


@dataclass
class ProxyInfo:
    """Proxy server configuration and metadata.

    Represents a proxy server with authentication, status tracking,
    and automatic format conversion for different use cases.

    Attributes:
        host: Proxy server hostname or IP address
        port: Proxy server port number
        protocol: Proxy protocol type (http, https, or socks5)
        username: Optional authentication username
        password: Optional authentication password
        geo: Optional geographical information about proxy location
        speed_ms: Optional proxy response time in milliseconds
        is_residential: Whether proxy is residential (vs datacenter)
        is_valid: Whether proxy is currently valid
        last_check: Timestamp of last validation check
        fail_count: Number of consecutive failures

    Example:
        >>> proxy = ProxyInfo(
        ...     host="proxy.example.com",
        ...     port=8080,
        ...     protocol="http",
        ...     username="user",
        ...     password="pass"
        ... )
        >>> print(proxy.url)
        http://user:pass@proxy.example.com:8080
    """

    host: str
    port: int
    protocol: Literal["http", "https", "socks5"] = "http"
    username: Optional[str] = None
    password: Optional[str] = None
    # Metadata (filled after validation)
    geo: Optional[GeoInfo] = None
    speed_ms: Optional[int] = None
    is_residential: bool = False
    # Status
    is_valid: bool = True
    last_check: Optional[datetime] = None
    fail_count: int = 0

    @property
    def url(self) -> str:
        """Generate full proxy URL with authentication.

        Returns:
            Complete proxy URL in format: protocol://[user:pass@]host:port

        Example:
            >>> proxy = ProxyInfo(host="proxy.com", port=8080, username="user", password="pass")
            >>> proxy.url
            'http://user:pass@proxy.com:8080'
        """
        if self.username and self.password:
            # URL-encode username and password to handle special characters
            encoded_user = quote(self.username, safe="")
            encoded_pass = quote(self.password, safe="")
            return f"{self.protocol}://{encoded_user}:{encoded_pass}@{self.host}:{self.port}"
        return f"{self.protocol}://{self.host}:{self.port}"

    @property
    def playwright_proxy(self) -> Dict[str, Any]:
        """Generate Playwright-compatible proxy configuration.

        Returns:
            Dictionary with Playwright proxy format

        Example:
            >>> proxy = ProxyInfo(host="proxy.com", port=8080, username="user", password="pass")
            >>> proxy.playwright_proxy
            {'server': 'http://proxy.com:8080', 'username': 'user', 'password': 'pass'}
        """
        config: Dict[str, Any] = {"server": f"{self.protocol}://{self.host}:{self.port}"}
        if self.username:
            config["username"] = self.username
        if self.password:
            config["password"] = self.password
        return config

    def mark_failed(self) -> None:
        """Mark proxy check as failed and update status.

        Increments fail_count and sets is_valid to False if fail_count exceeds 3.
        Updates last_check timestamp to current time.

        Example:
            >>> proxy = ProxyInfo(host="proxy.com", port=8080)
            >>> proxy.mark_failed()
            >>> proxy.fail_count
            1
            >>> proxy.is_valid
            True
            >>> for _ in range(3):
            ...     proxy.mark_failed()
            >>> proxy.is_valid
            False
        """
        self.fail_count += 1
        self.last_check = datetime.now()
        if self.fail_count > 3:
            self.is_valid = False

    def mark_valid(self, speed_ms: int) -> None:
        """Mark proxy as valid and update metrics.

        Resets fail_count, sets is_valid to True, updates speed measurement
        and last_check timestamp.

        Args:
            speed_ms: Response time in milliseconds

        Example:
            >>> proxy = ProxyInfo(host="proxy.com", port=8080)
            >>> proxy.fail_count = 5
            >>> proxy.is_valid = False
            >>> proxy.mark_valid(speed_ms=150)
            >>> proxy.is_valid
            True
            >>> proxy.fail_count
            0
            >>> proxy.speed_ms
            150
        """
        self.is_valid = True
        self.fail_count = 0
        self.speed_ms = speed_ms
        self.last_check = datetime.now()

    @classmethod
    def from_url(cls, url: str) -> "ProxyInfo":
        """Parse proxy from URL format.

        Parses proxy configuration from URL string in format:
        protocol://[username:password@]host:port

        Args:
            url: Proxy URL string

        Returns:
            ProxyInfo instance

        Raises:
            ValueError: If URL format is invalid or missing required components

        Example:
            >>> proxy = ProxyInfo.from_url("http://user:pass@proxy.com:8080")
            >>> proxy.host
            'proxy.com'
            >>> proxy.port
            8080
            >>> proxy.username
            'user'
        """
        parsed = urlparse(url)

        if not parsed.hostname:
            raise ValueError(f"Invalid proxy URL: missing hostname in {url}")

        if not parsed.port:
            raise ValueError(f"Invalid proxy URL: missing port in {url}")

        # Extract protocol, default to http
        protocol = parsed.scheme if parsed.scheme else "http"
        if protocol not in ("http", "https", "socks5"):
            raise ValueError(f"Invalid protocol: {protocol}. Must be http, https, or socks5")

        return cls(
            host=parsed.hostname,
            port=parsed.port,
            protocol=protocol,  # type: ignore
            username=parsed.username,
            password=parsed.password,
        )

    @classmethod
    def from_string(cls, s: str) -> "ProxyInfo":
        """Parse proxy from string format.

        Supports multiple formats:
        - "host:port"
        - "host:port:username:password"
        - "protocol://host:port"
        - "protocol://username:password@host:port"

        Args:
            s: Proxy string in one of the supported formats

        Returns:
            ProxyInfo instance

        Raises:
            ValueError: If string format is invalid

        Example:
            >>> proxy = ProxyInfo.from_string("proxy.com:8080:user:pass")
            >>> proxy.host
            'proxy.com'
            >>> proxy.port
            8080
            >>> proxy.username
            'user'

            >>> proxy2 = ProxyInfo.from_string("proxy.com:8080")
            >>> proxy2.host
            'proxy.com'
            >>> proxy2.username is None
            True
        """
        # If it looks like a URL (contains ://), use from_url
        if "://" in s:
            return cls.from_url(s)

        # Otherwise parse as colon-separated format
        parts = s.split(":")

        if len(parts) == 2:
            # Format: host:port
            host, port_str = parts
            return cls(host=host, port=int(port_str))

        elif len(parts) == 4:
            # Format: host:port:username:password
            host, port_str, username, password = parts
            return cls(
                host=host, port=int(port_str), username=username, password=password
            )

        else:
            raise ValueError(
                f"Invalid proxy string format: {s}. "
                "Expected 'host:port' or 'host:port:username:password'"
            )


__all__ = ["ProxyInfo"]
