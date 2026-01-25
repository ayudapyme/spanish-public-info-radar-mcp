"""Integration test fixtures.

Provides fixtures for integration tests that make real API calls.
"""

import pytest


@pytest.fixture
def skip_if_rate_limited():
    """Fixture to handle rate limiting in integration tests.

    Can be used to skip tests if rate limits are detected.
    """
    return True
