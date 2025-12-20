"""Identity and persona data structures.

This module defines the core data structures for representing browser personas,
including geographical information, device characteristics, and fingerprints.
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Literal, Optional
from uuid import uuid4


@dataclass
class GeoInfo:
    """Geographical and locale information for a persona.

    Represents the geographical location and language settings
    that will be used for the browser session.

    Attributes:
        country_code: ISO 3166-1 alpha-2 country code (e.g., "DE", "US", "FR")
        country: Full country name (e.g., "Germany", "United States")
        city: Optional city name (e.g., "Berlin", "New York")
        timezone: IANA timezone identifier (e.g., "Europe/Berlin", "America/New_York")
        language: Primary language code (e.g., "de-DE", "en-US")
        languages: List of accepted languages in preference order

    Example:
        >>> geo = GeoInfo(
        ...     country_code="DE",
        ...     country="Germany",
        ...     city="Berlin",
        ...     timezone="Europe/Berlin",
        ...     language="de-DE",
        ...     languages=["de-DE", "de", "en-US", "en"]
        ... )
    """

    country_code: str
    country: str
    city: Optional[str]
    timezone: str
    language: str
    languages: list[str]


@dataclass
class DeviceInfo:
    """Device and hardware information for fingerprinting.

    Represents the device characteristics that will be used to generate
    a unique and realistic browser fingerprint.

    Attributes:
        type: Device type - either "desktop" or "mobile"
        platform: Navigator.platform value (e.g., "Win32", "MacIntel", "Linux x86_64")
        vendor: GPU vendor string (e.g., "Google Inc.", "Apple Inc.")
        renderer: WebGL renderer string (e.g., "ANGLE (Intel, Mesa)")
        screen_width: Screen width in pixels
        screen_height: Screen height in pixels
        color_depth: Color depth in bits (default: 24)
        pixel_ratio: Device pixel ratio (default: 1.0)

    Example:
        >>> device = DeviceInfo(
        ...     type="desktop",
        ...     platform="Win32",
        ...     vendor="Google Inc.",
        ...     renderer="ANGLE (Intel, Mesa Intel(R) UHD Graphics 620)",
        ...     screen_width=1920,
        ...     screen_height=1080,
        ...     color_depth=24,
        ...     pixel_ratio=1.0
        ... )
    """

    type: Literal["desktop", "mobile"]
    platform: str
    vendor: str
    renderer: str
    screen_width: int
    screen_height: int
    color_depth: int = 24
    pixel_ratio: float = 1.0


@dataclass
class Fingerprint:
    """Browser fingerprint information.

    Combines various fingerprinting signals to create a unique
    and realistic browser identity.

    Attributes:
        user_agent: Browser User-Agent string
        device: Device information
        canvas_hash: Optional hash of Canvas fingerprint
        webgl_hash: Optional hash of WebGL fingerprint
        audio_hash: Optional hash of Audio fingerprint
        fonts: List of available fonts

    Example:
        >>> fingerprint = Fingerprint(
        ...     user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
        ...     device=device_info,
        ...     canvas_hash="a1b2c3d4",
        ...     webgl_hash="e5f6g7h8",
        ...     fonts=["Arial", "Times New Roman", "Courier New"]
        ... )
    """

    user_agent: str
    device: DeviceInfo
    canvas_hash: Optional[str] = None
    webgl_hash: Optional[str] = None
    audio_hash: Optional[str] = None
    fonts: list[str] = field(default_factory=list)


@dataclass
class Persona:
    """Complete persona representation for browser automation.

    A persona encapsulates all information needed to create a unique
    browser session, including fingerprint, geolocation, proxy settings,
    and session state.

    Attributes:
        id: Unique identifier for the persona (UUID4)
        fingerprint: Browser fingerprint information
        geo: Geographical and locale information
        proxy: Optional proxy configuration
        cookies: Dictionary of cookies to set
        local_storage: Dictionary of localStorage items
        created_at: Timestamp when persona was created
        last_used: Timestamp when persona was last used
        use_count: Number of times persona has been used
        is_burned: Flag indicating if persona is compromised/detected

    Example:
        >>> persona = Persona(
        ...     fingerprint=fingerprint,
        ...     geo=geo_info,
        ...     created_at=datetime.now()
        ... )
        >>> persona.mark_used()
        >>> persona.to_dict()
    """

    fingerprint: Fingerprint
    geo: GeoInfo
    created_at: datetime
    id: str = field(default_factory=lambda: str(uuid4()))
    proxy: Optional[Any] = None  # Will be ProxyInfo once defined
    cookies: dict[str, Any] = field(default_factory=dict)
    local_storage: dict[str, Any] = field(default_factory=dict)
    last_used: Optional[datetime] = None
    use_count: int = 0
    is_burned: bool = False

    def mark_used(self) -> None:
        """Mark the persona as used and update usage statistics.

        Updates the last_used timestamp to now and increments the use_count.
        This helps track persona usage patterns and detect if a persona
        is being overused.

        Example:
            >>> persona = Persona(...)
            >>> persona.mark_used()
            >>> persona.use_count
            1
            >>> persona.last_used
            datetime.datetime(2024, 1, 1, 12, 0, 0)
        """
        self.last_used = datetime.now()
        self.use_count += 1

    def burn(self) -> None:
        """Mark the persona as burned (compromised/detected).

        Once a persona is burned, it should not be used again as it has
        been detected by anti-bot systems or otherwise compromised.

        Example:
            >>> persona = Persona(...)
            >>> persona.burn()
            >>> persona.is_burned
            True
        """
        self.is_burned = True

    def to_dict(self) -> dict[str, Any]:
        """Convert persona to dictionary representation.

        Serializes the persona and all nested dataclasses to a dictionary
        format suitable for JSON serialization or storage.

        Returns:
            Dictionary representation of the persona

        Example:
            >>> persona = Persona(...)
            >>> data = persona.to_dict()
            >>> data["id"]
            "550e8400-e29b-41d4-a716-446655440000"
        """
        data = asdict(self)
        # Convert datetime objects to ISO format strings
        if self.created_at:
            data["created_at"] = self.created_at.isoformat()
        if self.last_used:
            data["last_used"] = self.last_used.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Persona":
        """Create Persona instance from dictionary.

        Deserializes a persona from dictionary format, handling nested
        dataclasses and datetime conversions.

        Args:
            data: Dictionary containing persona data

        Returns:
            Persona instance

        Example:
            >>> data = {
            ...     "id": "550e8400-e29b-41d4-a716-446655440000",
            ...     "fingerprint": {...},
            ...     "geo": {...},
            ...     "created_at": "2024-01-01T12:00:00"
            ... }
            >>> persona = Persona.from_dict(data)
        """
        # Create nested dataclasses
        fingerprint_data = data["fingerprint"]
        device_data = fingerprint_data["device"]

        device = DeviceInfo(**device_data)
        fingerprint_data["device"] = device
        fingerprint = Fingerprint(**fingerprint_data)

        geo = GeoInfo(**data["geo"])

        # Parse datetime strings
        created_at = (
            datetime.fromisoformat(data["created_at"])
            if isinstance(data["created_at"], str)
            else data["created_at"]
        )
        last_used = None
        if data.get("last_used"):
            last_used = (
                datetime.fromisoformat(data["last_used"])
                if isinstance(data["last_used"], str)
                else data["last_used"]
            )

        # Create persona with all fields
        return cls(
            id=data.get("id", str(uuid4())),
            fingerprint=fingerprint,
            geo=geo,
            proxy=data.get("proxy"),
            cookies=data.get("cookies", {}),
            local_storage=data.get("local_storage", {}),
            created_at=created_at,
            last_used=last_used,
            use_count=data.get("use_count", 0),
            is_burned=data.get("is_burned", False),
        )


__all__ = [
    "GeoInfo",
    "DeviceInfo",
    "Fingerprint",
    "Persona",
]
