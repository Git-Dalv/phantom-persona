"""Configuration schema using Pydantic v2.

This module defines the configuration models for phantom-persona using Pydantic v2,
providing validation, serialization, and type safety for all configuration options.
"""

from typing import List, Literal, Optional, Tuple

from pydantic import BaseModel, Field, field_validator


class BrowserConfig(BaseModel):
    """Browser configuration settings.

    Controls browser type, execution mode, and launch arguments.

    Attributes:
        type: Browser type to use (chromium, firefox, or webkit)
        headless: Whether to run browser in headless mode
        args: Additional command-line arguments for browser launch
        slow_mo: Slow down operations by specified milliseconds (for debugging)

    Example:
        >>> config = BrowserConfig(type="chromium", headless=True)
        >>> config.type
        'chromium'
    """

    type: Literal["chromium", "firefox", "webkit"] = Field(
        default="chromium", description="Browser type to use"
    )
    headless: bool = Field(default=True, description="Run browser in headless mode")
    args: List[str] = Field(default_factory=list, description="Additional launch arguments")
    slow_mo: int = Field(default=0, ge=0, description="Slow down operations in milliseconds")


class ProxyConfig(BaseModel):
    """Proxy configuration settings.

    Controls proxy usage, validation, and rotation strategies.

    Attributes:
        enabled: Whether to use proxy
        source: Path to proxy file or URL for proxy list
        rotation: Proxy rotation strategy
        validate_proxies: Whether to validate proxies before use
        geo_lookup: Whether to perform geographical lookup for proxies

    Example:
        >>> config = ProxyConfig(enabled=True, source="proxies.txt")
        >>> config.rotation
        'per_session'
    """

    enabled: bool = Field(default=False, description="Enable proxy usage")
    source: Optional[str] = Field(default=None, description="Path to proxy file or URL")
    rotation: Literal["per_session", "per_request", "manual"] = Field(
        default="per_session", description="Proxy rotation strategy"
    )
    validate_proxies: bool = Field(default=True, description="Validate proxies before use")
    geo_lookup: bool = Field(
        default=True, description="Perform geographical lookup for proxies"
    )


class FingerprintConfig(BaseModel):
    """Fingerprint generation configuration.

    Controls how browser fingerprints are generated and applied.

    Attributes:
        consistency: Fingerprint consistency level
            - auto: Automatic consistency based on protection level
            - strict: Strict consistency, all fingerprint aspects match
            - loose: Loose consistency, some randomization allowed
        device_type: Type of device to emulate

    Example:
        >>> config = FingerprintConfig(consistency="strict", device_type="desktop")
        >>> config.device_type
        'desktop'
    """

    consistency: Literal["auto", "strict", "loose"] = Field(
        default="auto", description="Fingerprint consistency level"
    )
    device_type: Literal["desktop", "mobile", "random"] = Field(
        default="desktop", description="Device type to emulate"
    )


class BehaviorConfig(BaseModel):
    """Human behavior emulation configuration.

    Controls how human-like behaviors are simulated.

    Attributes:
        human_delays: Whether to add random human-like delays
        delay_range: Range of delays in seconds (min, max)

    Example:
        >>> config = BehaviorConfig(human_delays=True, delay_range=(0.5, 2.0))
        >>> config.delay_range
        (0.5, 2.0)
    """

    human_delays: bool = Field(default=True, description="Add human-like delays")
    delay_range: Tuple[float, float] = Field(
        default=(0.3, 1.5), description="Delay range in seconds (min, max)"
    )

    @field_validator("delay_range")
    @classmethod
    def validate_delay_range(cls, v: Tuple[float, float]) -> Tuple[float, float]:
        """Validate that delay_range is valid.

        Args:
            v: Delay range tuple (min, max)

        Returns:
            Validated delay range

        Raises:
            ValueError: If min >= max or values are negative
        """
        min_delay, max_delay = v
        if min_delay < 0:
            raise ValueError("Minimum delay must be non-negative")
        if max_delay < 0:
            raise ValueError("Maximum delay must be non-negative")
        if min_delay >= max_delay:
            raise ValueError("Minimum delay must be less than maximum delay")
        return v


class RetryConfig(BaseModel):
    """Retry logic configuration.

    Controls how failed operations are retried.

    Attributes:
        enabled: Whether to enable automatic retries
        max_attempts: Maximum number of retry attempts
        backoff: Backoff strategy for retries
            - exponential: Exponential backoff (2^n seconds)
            - linear: Linear backoff (n seconds)
            - fixed: Fixed delay between retries

    Example:
        >>> config = RetryConfig(enabled=True, max_attempts=5, backoff="exponential")
        >>> config.max_attempts
        5
    """

    enabled: bool = Field(default=True, description="Enable automatic retries")
    max_attempts: int = Field(default=3, ge=1, le=10, description="Maximum retry attempts")
    backoff: Literal["exponential", "linear", "fixed"] = Field(
        default="exponential", description="Backoff strategy for retries"
    )


class PhantomConfig(BaseModel):
    """Main configuration for phantom-persona.

    Combines all configuration sections into a single model.

    Attributes:
        level: Protection level (0-4)
            - 0: Minimal protection
            - 1: Basic protection
            - 2: Standard protection (recommended)
            - 3: Enhanced protection
            - 4: Maximum protection
        browser: Browser configuration
        proxy: Proxy configuration
        fingerprint: Fingerprint configuration
        behavior: Behavior emulation configuration
        retry: Retry logic configuration

    Example:
        >>> config = PhantomConfig(level=2)
        >>> config.level
        2
        >>> config.browser.type
        'chromium'
    """

    level: int = Field(default=1, ge=0, le=4, description="Protection level (0-4)")
    browser: BrowserConfig = Field(default_factory=BrowserConfig, description="Browser settings")
    proxy: ProxyConfig = Field(default_factory=ProxyConfig, description="Proxy settings")
    fingerprint: FingerprintConfig = Field(
        default_factory=FingerprintConfig, description="Fingerprint settings"
    )
    behavior: BehaviorConfig = Field(
        default_factory=BehaviorConfig, description="Behavior emulation settings"
    )
    retry: RetryConfig = Field(default_factory=RetryConfig, description="Retry logic settings")

    @field_validator("level")
    @classmethod
    def validate_level(cls, v: int) -> int:
        """Validate protection level.

        Args:
            v: Protection level value

        Returns:
            Validated level

        Raises:
            ValueError: If level is not in range 0-4
        """
        if not 0 <= v <= 4:
            raise ValueError(f"Protection level must be between 0 and 4, got {v}")
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "level": 2,
                    "browser": {"type": "chromium", "headless": True},
                    "proxy": {"enabled": True, "source": "proxies.txt"},
                    "fingerprint": {"consistency": "strict", "device_type": "desktop"},
                    "behavior": {"human_delays": True, "delay_range": [0.3, 1.5]},
                    "retry": {"enabled": True, "max_attempts": 3, "backoff": "exponential"},
                }
            ]
        }
    }


__all__ = [
    "BrowserConfig",
    "ProxyConfig",
    "FingerprintConfig",
    "BehaviorConfig",
    "RetryConfig",
    "PhantomConfig",
]
