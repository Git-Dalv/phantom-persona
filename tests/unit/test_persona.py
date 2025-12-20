"""Unit tests for persona module.

Tests for Persona, GeoInfo, DeviceInfo, and Fingerprint dataclasses.
"""

from datetime import datetime
from time import sleep

import pytest

from phantom_persona.persona import DeviceInfo, Fingerprint, GeoInfo, Persona


# === Fixtures ===


@pytest.fixture
def sample_geo_info():
    """Sample GeoInfo for testing.

    Returns:
        GeoInfo instance with US location
    """
    return GeoInfo(
        country_code="US",
        country="United States",
        city="New York",
        timezone="America/New_York",
        language="en-US",
        languages=["en-US", "en"],
    )


@pytest.fixture
def sample_device_info():
    """Sample DeviceInfo for testing.

    Returns:
        DeviceInfo instance for desktop
    """
    return DeviceInfo(
        type="desktop",
        platform="Win32",
        vendor="Google Inc.",
        renderer="ANGLE (Intel, Mesa Intel(R) UHD Graphics 620)",
        screen_width=1920,
        screen_height=1080,
    )


@pytest.fixture
def sample_fingerprint(sample_device_info):
    """Sample Fingerprint for testing.

    Returns:
        Fingerprint instance with basic info
    """
    return Fingerprint(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        device=sample_device_info,
    )


@pytest.fixture
def sample_persona(sample_fingerprint, sample_geo_info):
    """Sample Persona for testing.

    Returns:
        Persona instance with all basic fields
    """
    return Persona(
        fingerprint=sample_fingerprint,
        geo=sample_geo_info,
        created_at=datetime.now(),
    )


# === Persona Tests ===


def test_persona_creation(sample_fingerprint, sample_geo_info):
    """Test Persona creation with required fields.

    Verifies:
    - Persona can be created with fingerprint, geo, and created_at
    - Required fields are set correctly
    - Optional fields have proper defaults
    """
    created_at = datetime.now()
    persona = Persona(
        fingerprint=sample_fingerprint,
        geo=sample_geo_info,
        created_at=created_at,
    )

    # Check required fields
    assert persona.fingerprint == sample_fingerprint
    assert persona.geo == sample_geo_info
    assert persona.created_at == created_at

    # Check optional field defaults
    assert persona.proxy is None
    assert persona.cookies == {}
    assert persona.local_storage == {}
    assert persona.last_used is None
    assert persona.use_count == 0
    assert persona.is_burned is False


def test_persona_default_id():
    """Test that Persona ID is generated automatically.

    Verifies:
    - ID is generated if not provided
    - ID is a valid UUID string
    - Each persona gets a unique ID
    """
    geo = GeoInfo(
        country_code="US",
        country="USA",
        city=None,
        timezone="America/New_York",
        language="en",
        languages=["en"],
    )
    device = DeviceInfo(
        type="desktop",
        platform="Win32",
        vendor="Google",
        renderer="ANGLE",
        screen_width=1920,
        screen_height=1080,
    )
    fingerprint = Fingerprint(user_agent="Mozilla/5.0", device=device)

    # Create two personas without specifying ID
    persona1 = Persona(fingerprint=fingerprint, geo=geo, created_at=datetime.now())
    persona2 = Persona(fingerprint=fingerprint, geo=geo, created_at=datetime.now())

    # Check IDs are generated
    assert persona1.id is not None
    assert persona2.id is not None
    assert isinstance(persona1.id, str)
    assert isinstance(persona2.id, str)

    # Check IDs are unique
    assert persona1.id != persona2.id

    # Check ID format (UUID4 has 5 groups separated by dashes)
    assert len(persona1.id.split("-")) == 5


def test_persona_mark_used(sample_persona):
    """Test Persona.mark_used() updates statistics.

    Verifies:
    - last_used is set to current time
    - use_count is incremented
    - Multiple calls increment use_count correctly
    """
    # Initial state
    assert sample_persona.last_used is None
    assert sample_persona.use_count == 0

    # Mark as used once
    before = datetime.now()
    sample_persona.mark_used()
    after = datetime.now()

    assert sample_persona.last_used is not None
    assert before <= sample_persona.last_used <= after
    assert sample_persona.use_count == 1

    # Mark as used again
    sleep(0.01)  # Small delay to ensure different timestamp
    first_use = sample_persona.last_used
    sample_persona.mark_used()

    assert sample_persona.last_used > first_use
    assert sample_persona.use_count == 2

    # Mark as used third time
    sample_persona.mark_used()
    assert sample_persona.use_count == 3


def test_persona_burn(sample_persona):
    """Test Persona.burn() marks persona as compromised.

    Verifies:
    - is_burned is set to True
    - Persona state is updated
    """
    # Initial state
    assert sample_persona.is_burned is False

    # Burn the persona
    sample_persona.burn()

    # Verify burned state
    assert sample_persona.is_burned is True

    # Burning again should not cause issues
    sample_persona.burn()
    assert sample_persona.is_burned is True


def test_persona_to_dict(sample_persona):
    """Test Persona.to_dict() serialization.

    Verifies:
    - Persona is converted to dictionary
    - All fields are present
    - Nested dataclasses are converted
    - Datetimes are converted to ISO format strings
    """
    persona_dict = sample_persona.to_dict()

    # Check it's a dict
    assert isinstance(persona_dict, dict)

    # Check top-level fields
    assert "id" in persona_dict
    assert "fingerprint" in persona_dict
    assert "geo" in persona_dict
    assert "proxy" in persona_dict
    assert "cookies" in persona_dict
    assert "local_storage" in persona_dict
    assert "created_at" in persona_dict
    assert "last_used" in persona_dict
    assert "use_count" in persona_dict
    assert "is_burned" in persona_dict

    # Check nested structures
    assert isinstance(persona_dict["fingerprint"], dict)
    assert isinstance(persona_dict["geo"], dict)
    assert "user_agent" in persona_dict["fingerprint"]
    assert "device" in persona_dict["fingerprint"]
    assert "country" in persona_dict["geo"]

    # Check datetime conversion
    assert isinstance(persona_dict["created_at"], str)
    assert "T" in persona_dict["created_at"]  # ISO format has T separator


def test_persona_from_dict(sample_persona):
    """Test Persona.from_dict() deserialization.

    Verifies:
    - Persona can be reconstructed from dict
    - All fields are restored correctly
    - Roundtrip (to_dict -> from_dict) preserves data
    """
    # Serialize to dict
    persona_dict = sample_persona.to_dict()

    # Deserialize back to Persona
    restored_persona = Persona.from_dict(persona_dict)

    # Check fields match
    assert restored_persona.id == sample_persona.id
    assert restored_persona.fingerprint.user_agent == sample_persona.fingerprint.user_agent
    assert restored_persona.geo.country == sample_persona.geo.country
    assert restored_persona.geo.city == sample_persona.geo.city
    assert restored_persona.use_count == sample_persona.use_count
    assert restored_persona.is_burned == sample_persona.is_burned

    # Check datetime fields
    assert restored_persona.created_at == sample_persona.created_at
    assert restored_persona.last_used == sample_persona.last_used


def test_persona_roundtrip_with_usage(sample_persona):
    """Test Persona roundtrip after marking as used.

    Verifies:
    - Persona with usage stats can be serialized and restored
    - Usage statistics are preserved
    """
    # Mark as used
    sample_persona.mark_used()
    sample_persona.mark_used()

    # Roundtrip
    persona_dict = sample_persona.to_dict()
    restored = Persona.from_dict(persona_dict)

    # Verify usage stats preserved
    assert restored.use_count == 2
    assert restored.last_used is not None
    assert restored.last_used == sample_persona.last_used


def test_persona_roundtrip_with_cookies():
    """Test Persona roundtrip with cookies and local storage.

    Verifies:
    - Cookies and localStorage are preserved
    """
    geo = GeoInfo(
        country_code="DE",
        country="Germany",
        city="Berlin",
        timezone="Europe/Berlin",
        language="de-DE",
        languages=["de-DE", "de", "en"],
    )
    device = DeviceInfo(
        type="desktop",
        platform="Linux x86_64",
        vendor="Intel",
        renderer="Mesa",
        screen_width=1920,
        screen_height=1080,
    )
    fingerprint = Fingerprint(user_agent="Mozilla/5.0", device=device)

    persona = Persona(
        fingerprint=fingerprint,
        geo=geo,
        created_at=datetime.now(),
        cookies={"session": "abc123", "tracking": "xyz789"},
        local_storage={"theme": "dark", "lang": "de"},
    )

    # Roundtrip
    persona_dict = persona.to_dict()
    restored = Persona.from_dict(persona_dict)

    assert restored.cookies == {"session": "abc123", "tracking": "xyz789"}
    assert restored.local_storage == {"theme": "dark", "lang": "de"}


# === GeoInfo Tests ===


def test_geo_info_creation():
    """Test GeoInfo creation with all fields.

    Verifies:
    - GeoInfo can be created with all required fields
    - All fields are set correctly
    - Optional city field works
    """
    geo = GeoInfo(
        country_code="GB",
        country="United Kingdom",
        city="London",
        timezone="Europe/London",
        language="en-GB",
        languages=["en-GB", "en"],
    )

    assert geo.country_code == "GB"
    assert geo.country == "United Kingdom"
    assert geo.city == "London"
    assert geo.timezone == "Europe/London"
    assert geo.language == "en-GB"
    assert geo.languages == ["en-GB", "en"]


def test_geo_info_without_city():
    """Test GeoInfo with None city.

    Verifies:
    - City is optional and can be None
    """
    geo = GeoInfo(
        country_code="FR",
        country="France",
        city=None,
        timezone="Europe/Paris",
        language="fr-FR",
        languages=["fr-FR", "fr"],
    )

    assert geo.city is None
    assert geo.country == "France"


def test_geo_info_multiple_languages():
    """Test GeoInfo with multiple language preferences.

    Verifies:
    - languages list can contain multiple entries
    - Order is preserved
    """
    geo = GeoInfo(
        country_code="CH",
        country="Switzerland",
        city="Zurich",
        timezone="Europe/Zurich",
        language="de-CH",
        languages=["de-CH", "fr-CH", "it-CH", "en"],
    )

    assert len(geo.languages) == 4
    assert geo.languages[0] == "de-CH"
    assert geo.languages[-1] == "en"


# === DeviceInfo Tests ===


def test_device_info_defaults():
    """Test DeviceInfo default values.

    Verifies:
    - color_depth defaults to 24
    - pixel_ratio defaults to 1.0
    - Other fields are set correctly
    """
    device = DeviceInfo(
        type="desktop",
        platform="MacIntel",
        vendor="Apple Inc.",
        renderer="Apple M1",
        screen_width=2560,
        screen_height=1440,
    )

    # Check required fields
    assert device.type == "desktop"
    assert device.platform == "MacIntel"
    assert device.vendor == "Apple Inc."
    assert device.renderer == "Apple M1"
    assert device.screen_width == 2560
    assert device.screen_height == 1440

    # Check defaults
    assert device.color_depth == 24
    assert device.pixel_ratio == 1.0


def test_device_info_custom_defaults():
    """Test DeviceInfo with custom color_depth and pixel_ratio.

    Verifies:
    - Defaults can be overridden
    """
    device = DeviceInfo(
        type="mobile",
        platform="iPhone",
        vendor="Apple Inc.",
        renderer="Apple GPU",
        screen_width=390,
        screen_height=844,
        color_depth=32,
        pixel_ratio=3.0,
    )

    assert device.color_depth == 32
    assert device.pixel_ratio == 3.0


def test_device_info_mobile_type():
    """Test DeviceInfo with mobile type.

    Verifies:
    - type can be "mobile"
    - Mobile-specific configurations work
    """
    device = DeviceInfo(
        type="mobile",
        platform="Linux armv8l",
        vendor="Qualcomm",
        renderer="Adreno",
        screen_width=1080,
        screen_height=2400,
        pixel_ratio=2.625,
    )

    assert device.type == "mobile"
    assert device.screen_width == 1080
    assert device.pixel_ratio == 2.625


# === Fingerprint Tests ===


def test_fingerprint_optional_fields():
    """Test Fingerprint optional fields default to None.

    Verifies:
    - canvas_hash defaults to None
    - webgl_hash defaults to None
    - audio_hash defaults to None
    - fonts defaults to empty list
    """
    device = DeviceInfo(
        type="desktop",
        platform="Win32",
        vendor="NVIDIA",
        renderer="GeForce GTX",
        screen_width=1920,
        screen_height=1080,
    )

    fingerprint = Fingerprint(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        device=device,
    )

    # Check optional fields
    assert fingerprint.canvas_hash is None
    assert fingerprint.webgl_hash is None
    assert fingerprint.audio_hash is None
    assert fingerprint.fonts == []


def test_fingerprint_with_hashes():
    """Test Fingerprint with all hash fields set.

    Verifies:
    - Hash fields can be set
    - All values are stored correctly
    """
    device = DeviceInfo(
        type="desktop",
        platform="Win32",
        vendor="AMD",
        renderer="Radeon",
        screen_width=1920,
        screen_height=1080,
    )

    fingerprint = Fingerprint(
        user_agent="Mozilla/5.0",
        device=device,
        canvas_hash="abc123def456",
        webgl_hash="ghi789jkl012",
        audio_hash="mno345pqr678",
    )

    assert fingerprint.canvas_hash == "abc123def456"
    assert fingerprint.webgl_hash == "ghi789jkl012"
    assert fingerprint.audio_hash == "mno345pqr678"


def test_fingerprint_with_fonts():
    """Test Fingerprint with fonts list.

    Verifies:
    - fonts list can be populated
    - Multiple fonts are stored
    """
    device = DeviceInfo(
        type="desktop",
        platform="Win32",
        vendor="Intel",
        renderer="Intel HD",
        screen_width=1366,
        screen_height=768,
    )

    fonts = ["Arial", "Times New Roman", "Courier New", "Verdana", "Georgia"]
    fingerprint = Fingerprint(
        user_agent="Mozilla/5.0",
        device=device,
        fonts=fonts,
    )

    assert len(fingerprint.fonts) == 5
    assert "Arial" in fingerprint.fonts
    assert "Georgia" in fingerprint.fonts


def test_fingerprint_complete():
    """Test Fingerprint with all fields populated.

    Verifies:
    - Complete fingerprint can be created
    - All fields are set correctly
    """
    device = DeviceInfo(
        type="desktop",
        platform="MacIntel",
        vendor="Apple Inc.",
        renderer="Apple M2",
        screen_width=2880,
        screen_height=1800,
        color_depth=24,
        pixel_ratio=2.0,
    )

    fingerprint = Fingerprint(
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        device=device,
        canvas_hash="canvas_abc123",
        webgl_hash="webgl_def456",
        audio_hash="audio_ghi789",
        fonts=["SF Pro", "Helvetica Neue", "Arial"],
    )

    assert fingerprint.user_agent.startswith("Mozilla/5.0")
    assert fingerprint.device.type == "desktop"
    assert fingerprint.canvas_hash == "canvas_abc123"
    assert fingerprint.webgl_hash == "webgl_def456"
    assert fingerprint.audio_hash == "audio_ghi789"
    assert len(fingerprint.fonts) == 3


# === Integration Tests ===


def test_complete_persona_workflow():
    """Test complete workflow: create, use, serialize, restore.

    Verifies:
    - Complete persona lifecycle works
    - All operations preserve data correctly
    """
    # Create complete persona
    geo = GeoInfo(
        country_code="JP",
        country="Japan",
        city="Tokyo",
        timezone="Asia/Tokyo",
        language="ja-JP",
        languages=["ja-JP", "ja", "en"],
    )

    device = DeviceInfo(
        type="desktop",
        platform="Win32",
        vendor="NVIDIA Corporation",
        renderer="NVIDIA GeForce RTX 3080",
        screen_width=3840,
        screen_height=2160,
        pixel_ratio=1.5,
    )

    fingerprint = Fingerprint(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        device=device,
        canvas_hash="jp_canvas_hash",
        webgl_hash="jp_webgl_hash",
        fonts=["MS Gothic", "Yu Gothic", "Meiryo"],
    )

    persona = Persona(
        fingerprint=fingerprint,
        geo=geo,
        created_at=datetime.now(),
        cookies={"sid": "session123"},
        local_storage={"pref": "dark"},
    )

    # Use persona
    persona.mark_used()
    persona.mark_used()

    # Serialize
    data = persona.to_dict()

    # Restore
    restored = Persona.from_dict(data)

    # Verify
    assert restored.geo.country == "Japan"
    assert restored.use_count == 2
    assert restored.cookies == {"sid": "session123"}
    assert restored.fingerprint.fonts == ["MS Gothic", "Yu Gothic", "Meiryo"]
    assert restored.is_burned is False

    # Burn and verify
    restored.burn()
    assert restored.is_burned is True
