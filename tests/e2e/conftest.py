"""Pytest configuration for E2E tests."""

import pytest


def pytest_configure(config):
    """Configure pytest for E2E tests."""
    config.addinivalue_line(
        "markers",
        "e2e: mark test as end-to-end test requiring internet connection"
    )
    config.addinivalue_line(
        "markers",
        "slow: mark test as slow running test (>5 seconds)"
    )


def pytest_collection_modifyitems(config, items):
    """Auto-add markers to tests based on location."""
    for item in items:
        # Auto-mark all tests in e2e directory as e2e tests
        if "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
