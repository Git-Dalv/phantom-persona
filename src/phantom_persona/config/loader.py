"""Configuration loader for phantom-persona.

This module provides utilities for loading configuration from various sources
including YAML files, JSON files, and dictionaries.
"""

import json
from pathlib import Path
from typing import Any, Union

import yaml
from pydantic import ValidationError

from phantom_persona.config.schema import PhantomConfig
from phantom_persona.core.exceptions import ConfigNotFoundError, ConfigValidationError


class ConfigLoader:
    """Configuration loader for phantom-persona.

    Provides static methods for loading configuration from various sources
    and creating configurations based on protection levels.

    Example:
        >>> # Load from YAML file
        >>> config = ConfigLoader.load("config.yaml")

        >>> # Load from dict
        >>> config = ConfigLoader.load({"level": 2, "browser": {"headless": True}})

        >>> # Create from protection level
        >>> config = ConfigLoader.from_level(3)
    """

    @staticmethod
    def load(source: Union[str, Path, dict[str, Any]]) -> PhantomConfig:
        """Load configuration from various sources.

        Automatically detects the source type and loads configuration:
        - str/Path: Loads from file (YAML or JSON based on extension)
        - dict: Uses the dictionary directly

        Args:
            source: Configuration source (file path or dictionary)

        Returns:
            Validated PhantomConfig instance

        Raises:
            ConfigNotFoundError: If file path doesn't exist
            ConfigValidationError: If configuration validation fails

        Example:
            >>> config = ConfigLoader.load("config.yaml")
            >>> config = ConfigLoader.load({"level": 2})
        """
        # Handle dictionary input
        if isinstance(source, dict):
            config_dict = source
        else:
            # Convert to Path
            path = Path(source)

            # Check if file exists
            if not path.exists():
                raise ConfigNotFoundError(
                    f"Configuration file not found: {path}",
                    details={"path": str(path)},
                )

            # Determine file type by extension
            suffix = path.suffix.lower()
            if suffix in (".yaml", ".yml"):
                config_dict = ConfigLoader.load_yaml(path)
            elif suffix == ".json":
                config_dict = ConfigLoader.load_json(path)
            else:
                raise ConfigValidationError(
                    f"Unsupported file format: {suffix}",
                    details={"path": str(path), "supported": [".yaml", ".yml", ".json"]},
                )

        # Merge with defaults
        config_dict = ConfigLoader.merge_with_defaults(config_dict)

        # Validate with Pydantic
        try:
            return PhantomConfig.model_validate(config_dict)
        except ValidationError as e:
            raise ConfigValidationError(
                "Configuration validation failed",
                details={"errors": e.errors()},
            ) from e

    @staticmethod
    def load_yaml(path: Path) -> dict[str, Any]:
        """Load configuration from YAML file.

        Args:
            path: Path to YAML file

        Returns:
            Dictionary containing configuration

        Raises:
            ConfigValidationError: If YAML parsing fails

        Example:
            >>> config_dict = ConfigLoader.load_yaml(Path("config.yaml"))
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                return data if data is not None else {}
        except yaml.YAMLError as e:
            raise ConfigValidationError(
                f"Failed to parse YAML file: {path}",
                details={"path": str(path), "error": str(e)},
            ) from e
        except OSError as e:
            raise ConfigNotFoundError(
                f"Failed to read file: {path}",
                details={"path": str(path), "error": str(e)},
            ) from e

    @staticmethod
    def load_json(path: Path) -> dict[str, Any]:
        """Load configuration from JSON file.

        Args:
            path: Path to JSON file

        Returns:
            Dictionary containing configuration

        Raises:
            ConfigValidationError: If JSON parsing fails

        Example:
            >>> config_dict = ConfigLoader.load_json(Path("config.json"))
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigValidationError(
                f"Failed to parse JSON file: {path}",
                details={"path": str(path), "error": str(e)},
            ) from e
        except OSError as e:
            raise ConfigNotFoundError(
                f"Failed to read file: {path}",
                details={"path": str(path), "error": str(e)},
            ) from e

    @staticmethod
    def merge_with_defaults(config: dict[str, Any]) -> dict[str, Any]:
        """Merge configuration with default values.

        This method ensures that all required fields have values,
        filling in defaults where necessary. Pydantic will handle
        the actual merging, so this just returns the config as-is.

        Args:
            config: Configuration dictionary

        Returns:
            Configuration dictionary (Pydantic handles defaults)

        Example:
            >>> config = ConfigLoader.merge_with_defaults({"level": 2})
            >>> config["level"]
            2
        """
        # Pydantic handles defaults automatically during validation
        # This method is provided for potential future custom logic
        return config

    @classmethod
    def from_level(cls, level: int) -> PhantomConfig:
        """Create configuration from protection level.

        Creates a PhantomConfig instance with default settings
        appropriate for the specified protection level.

        Args:
            level: Protection level (0-4)

        Returns:
            PhantomConfig instance configured for the protection level

        Raises:
            ConfigValidationError: If level is invalid

        Example:
            >>> config = ConfigLoader.from_level(2)
            >>> config.level
            2
            >>> config.browser.headless
            True
        """
        try:
            return PhantomConfig(level=level)
        except ValidationError as e:
            raise ConfigValidationError(
                f"Invalid protection level: {level}",
                details={"level": level, "errors": e.errors()},
            ) from e


__all__ = ["ConfigLoader"]
