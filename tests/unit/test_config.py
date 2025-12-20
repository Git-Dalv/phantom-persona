"""Unit tests for configuration module.

Tests for PhantomConfig, ConfigLoader, and ProtectionLevel.
"""

import json
import tempfile
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from phantom_persona.config import (
    BehaviorConfig,
    BrowserConfig,
    ConfigLoader,
    FingerprintConfig,
    PhantomConfig,
    ProtectionLevel,
    ProxyConfig,
    RetryConfig,
    get_level_description,
    get_plugins_for_level,
)
from phantom_persona.core.exceptions import ConfigNotFoundError, ConfigValidationError


# === Fixtures ===


@pytest.fixture
def temp_yaml_file():
    """Create a temporary YAML file for testing.

    Yields:
        Path to temporary YAML file
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def temp_json_file():
    """Create a temporary JSON file for testing.

    Yields:
        Path to temporary JSON file
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def sample_config_dict():
    """Sample configuration dictionary for testing.

    Returns:
        Dictionary with complete config
    """
    return {
        "level": 2,
        "browser": {
            "type": "chromium",
            "headless": True,
            "args": ["--no-sandbox"],
            "slow_mo": 50,
        },
        "proxy": {
            "enabled": True,
            "source": "proxies.txt",
            "rotation": "per_session",
            "validate_proxies": True,
            "geo_lookup": True,
        },
        "fingerprint": {
            "consistency": "strict",
            "device_type": "desktop",
        },
        "behavior": {
            "human_delays": True,
            "delay_range": [0.1, 0.5],
        },
        "retry": {
            "enabled": True,
            "max_attempts": 5,
            "backoff": "exponential",
        },
    }


@pytest.fixture
def partial_config_dict():
    """Partial configuration dictionary for testing merge with defaults.

    Returns:
        Dictionary with only level and browser config
    """
    return {
        "level": 3,
        "browser": {
            "headless": False,
        },
    }


# === Tests ===


def test_default_config_creation():
    """Test PhantomConfig creation with default values.

    Verifies:
    - Config can be created without arguments
    - All default values are set correctly
    - Level defaults to 1
    - All nested configs have defaults
    """
    config = PhantomConfig()

    # Check default level
    assert config.level == 1

    # Check browser defaults
    assert config.browser.type == "chromium"
    assert config.browser.headless is True
    assert config.browser.args == []
    assert config.browser.slow_mo == 0

    # Check proxy defaults
    assert config.proxy.enabled is False
    assert config.proxy.source is None
    assert config.proxy.rotation == "per_session"
    assert config.proxy.validate_proxies is True
    assert config.proxy.geo_lookup is True

    # Check fingerprint defaults
    assert config.fingerprint.consistency == "auto"
    assert config.fingerprint.device_type == "desktop"

    # Check behavior defaults
    assert config.behavior.human_delays is True
    assert config.behavior.delay_range == (0.3, 1.5)

    # Check retry defaults
    assert config.retry.enabled is True
    assert config.retry.max_attempts == 3
    assert config.retry.backoff == "exponential"


def test_config_from_dict(sample_config_dict):
    """Test loading config from dictionary.

    Verifies:
    - ConfigLoader.load() accepts dict
    - All values are correctly loaded
    - Nested configs are properly instantiated
    """
    config = ConfigLoader.load(sample_config_dict)

    # Check top level
    assert config.level == 2

    # Check browser config
    assert config.browser.type == "chromium"
    assert config.browser.headless is True
    assert config.browser.args == ["--no-sandbox"]
    assert config.browser.slow_mo == 50

    # Check proxy config
    assert config.proxy.enabled is True
    assert config.proxy.source == "proxies.txt"
    assert config.proxy.rotation == "per_session"
    assert config.proxy.validate_proxies is True

    # Check fingerprint config
    assert config.fingerprint.consistency == "strict"
    assert config.fingerprint.device_type == "desktop"

    # Check behavior config
    assert config.behavior.human_delays is True
    assert config.behavior.delay_range == (0.1, 0.5)

    # Check retry config
    assert config.retry.enabled is True
    assert config.retry.max_attempts == 5
    assert config.retry.backoff == "exponential"


def test_config_from_yaml(temp_yaml_file, sample_config_dict):
    """Test loading config from YAML file.

    Verifies:
    - ConfigLoader.load() accepts Path/str to YAML file
    - YAML is correctly parsed
    - Config values match expected values
    """
    # Write sample config to YAML file
    with open(temp_yaml_file, "w") as f:
        yaml.dump(sample_config_dict, f)

    # Load from file path (as Path)
    config_from_path = ConfigLoader.load(temp_yaml_file)
    assert config_from_path.level == 2
    assert config_from_path.browser.headless is True

    # Load from file path (as str)
    config_from_str = ConfigLoader.load(str(temp_yaml_file))
    assert config_from_str.level == 2
    assert config_from_str.browser.headless is True

    # Verify all values loaded correctly
    assert config_from_path.proxy.enabled is True
    assert config_from_path.fingerprint.consistency == "strict"
    assert config_from_path.behavior.delay_range == (0.1, 0.5)


def test_config_from_json(temp_json_file, sample_config_dict):
    """Test loading config from JSON file.

    Verifies:
    - ConfigLoader.load() accepts JSON files
    - JSON is correctly parsed
    """
    # Write sample config to JSON file
    with open(temp_json_file, "w") as f:
        json.dump(sample_config_dict, f)

    # Load from JSON file
    config = ConfigLoader.load(temp_json_file)

    assert config.level == 2
    assert config.browser.type == "chromium"
    assert config.proxy.enabled is True


def test_config_validation_level_valid():
    """Test that valid protection levels (0-4) are accepted.

    Verifies:
    - Levels 0, 1, 2, 3, 4 are all valid
    - No validation errors raised
    """
    for level in range(5):
        config = PhantomConfig(level=level)
        assert config.level == level


def test_config_validation_level_invalid():
    """Test that invalid protection levels raise validation error.

    Verifies:
    - Level < 0 raises ValidationError
    - Level > 4 raises ValidationError
    """
    # Test level too low
    with pytest.raises(ValidationError) as exc_info:
        PhantomConfig(level=-1)
    assert "level" in str(exc_info.value).lower()

    # Test level too high
    with pytest.raises(ValidationError) as exc_info:
        PhantomConfig(level=5)
    assert "level" in str(exc_info.value).lower()


def test_config_merge_with_defaults(partial_config_dict):
    """Test that partial config merges with defaults.

    Verifies:
    - Only specified values are overridden
    - Unspecified values use defaults
    - Partial nested configs work correctly
    """
    config = ConfigLoader.load(partial_config_dict)

    # Check overridden values
    assert config.level == 3
    assert config.browser.headless is False

    # Check values that should be defaults
    assert config.browser.type == "chromium"  # default
    assert config.browser.args == []  # default
    assert config.browser.slow_mo == 0  # default

    # Check that other sections use defaults
    assert config.proxy.enabled is False  # default
    assert config.fingerprint.consistency == "auto"  # default
    assert config.behavior.human_delays is True  # default
    assert config.retry.max_attempts == 3  # default


def test_config_from_level():
    """Test creating config from protection level.

    Verifies:
    - ConfigLoader.from_level() creates valid config
    - Level is set correctly
    - All other settings use defaults
    """
    for level in range(5):
        config = ConfigLoader.from_level(level)
        assert config.level == level
        assert isinstance(config, PhantomConfig)
        assert config.browser.type == "chromium"


def test_protection_level_enum_values():
    """Test ProtectionLevel enum values and names.

    Verifies:
    - All 5 levels exist (NONE, BASIC, MODERATE, ADVANCED, STEALTH)
    - Values are correct (0-4)
    - Names match expected names
    """
    # Test enum values
    assert ProtectionLevel.NONE == 0
    assert ProtectionLevel.BASIC == 1
    assert ProtectionLevel.MODERATE == 2
    assert ProtectionLevel.ADVANCED == 3
    assert ProtectionLevel.STEALTH == 4

    # Test enum names
    assert ProtectionLevel.NONE.name == "NONE"
    assert ProtectionLevel.BASIC.name == "BASIC"
    assert ProtectionLevel.MODERATE.name == "MODERATE"
    assert ProtectionLevel.ADVANCED.name == "ADVANCED"
    assert ProtectionLevel.STEALTH.name == "STEALTH"

    # Test all members exist
    assert len(ProtectionLevel) == 5


def test_get_plugins_for_level_basic():
    """Test get_plugins_for_level() for BASIC level.

    Verifies:
    - Returns list of plugin names
    - Contains expected basic plugins
    """
    plugins = get_plugins_for_level(ProtectionLevel.BASIC)

    assert isinstance(plugins, list)
    assert len(plugins) > 0
    assert "stealth.basic" in plugins


def test_get_plugins_for_level_all_levels():
    """Test get_plugins_for_level() for all levels.

    Verifies:
    - Each level returns a list
    - NONE level has minimal/no plugins
    """
    plugins_none = get_plugins_for_level(ProtectionLevel.NONE)
    plugins_basic = get_plugins_for_level(ProtectionLevel.BASIC)

    # All should return lists
    assert isinstance(plugins_none, list)
    assert isinstance(plugins_basic, list)

    # NONE should have fewest plugins
    assert len(plugins_none) <= len(plugins_basic)


def test_get_level_description():
    """Test get_level_description() for all levels.

    Verifies:
    - Returns string description for each level
    - Description is non-empty
    """
    for level in ProtectionLevel:
        description = get_level_description(level)
        assert isinstance(description, str)
        assert len(description) > 0


def test_behavior_config_delay_range_validation():
    """Test BehaviorConfig delay_range validation.

    Verifies:
    - delay_range must be a tuple of two floats
    - min must be less than max
    """
    # Valid range
    config = BehaviorConfig(delay_range=(0.1, 0.5))
    assert config.delay_range == (0.1, 0.5)

    # Invalid: min > max should fail validation
    with pytest.raises(ValidationError):
        BehaviorConfig(delay_range=(0.5, 0.1))


def test_browser_config_type():
    """Test BrowserConfig type values.

    Verifies:
    - Accepts valid browser types
    - Default is chromium
    """
    # Default
    config = BrowserConfig()
    assert config.type == "chromium"

    # Custom browser types
    for browser_type in ["chromium", "firefox", "webkit"]:
        config = BrowserConfig(type=browser_type)
        assert config.type == browser_type


def test_proxy_config_rotation_values():
    """Test ProxyConfig rotation strategy values.

    Verifies:
    - Accepts valid rotation strategies
    - Default is per_session
    """
    # Default
    config = ProxyConfig()
    assert config.rotation == "per_session"

    # Valid values
    for rotation in ["per_session", "per_request", "manual"]:
        config = ProxyConfig(rotation=rotation)
        assert config.rotation == rotation


def test_config_dict_export():
    """Test exporting config to dictionary.

    Verifies:
    - Can export to dict using model_dump()
    - All fields are present
    - Nested configs are properly exported
    """
    config = PhantomConfig(level=2)
    config_dict = config.model_dump()

    assert isinstance(config_dict, dict)
    assert "level" in config_dict
    assert "browser" in config_dict
    assert "proxy" in config_dict
    assert "fingerprint" in config_dict
    assert "behavior" in config_dict
    assert "retry" in config_dict

    # Check nested dict
    assert isinstance(config_dict["browser"], dict)
    assert "type" in config_dict["browser"]


def test_config_json_serialization():
    """Test JSON serialization of config.

    Verifies:
    - Can serialize to JSON string
    - Can deserialize from JSON string
    """
    original_config = PhantomConfig(level=3)

    # Serialize to JSON
    json_str = original_config.model_dump_json()
    assert isinstance(json_str, str)

    # Deserialize from JSON
    config_dict = json.loads(json_str)
    restored_config = PhantomConfig(**config_dict)

    assert restored_config.level == original_config.level
    assert restored_config.browser.type == original_config.browser.type


def test_config_with_none_values():
    """Test config with None values for optional fields.

    Verifies:
    - Optional fields can be None
    - Config is still valid
    """
    config = PhantomConfig(
        proxy=ProxyConfig(
            enabled=True,
            source=None,  # Optional field
        )
    )

    assert config.proxy.source is None
    assert config.proxy.enabled is True


def test_config_loader_invalid_path():
    """Test ConfigLoader with non-existent file.

    Verifies:
    - Raises ConfigNotFoundError for missing file
    """
    with pytest.raises(ConfigNotFoundError):
        ConfigLoader.load("/nonexistent/path/to/config.yaml")


def test_config_loader_invalid_yaml(temp_yaml_file):
    """Test ConfigLoader with invalid YAML content.

    Verifies:
    - Raises ConfigValidationError for malformed YAML
    """
    # Write invalid YAML
    temp_yaml_file.write_text("invalid: yaml: content: [unclosed")

    with pytest.raises(ConfigValidationError):
        ConfigLoader.load(temp_yaml_file)


def test_empty_config_dict():
    """Test loading empty config dict uses all defaults.

    Verifies:
    - Empty dict creates valid config
    - All values are defaults
    """
    config = ConfigLoader.load({})

    assert config.level == 1  # default
    assert config.browser.type == "chromium"  # default
    assert config.proxy.enabled is False  # default
