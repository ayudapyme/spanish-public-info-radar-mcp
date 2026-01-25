"""Shared pytest fixtures for Public Radar tests."""

from pathlib import Path

import pytest


def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line("markers", "integration: mark test as integration test (makes real API calls)")
    config.addinivalue_line("markers", "slow: mark test as slow (downloads large files)")


@pytest.fixture
def fixtures_dir() -> Path:
    """Return path to test fixtures directory.

    :return: Path to fixtures directory.
    :rtype: Path
    """
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_company_names() -> list[str]:
    """Sample company names for normalization tests.

    :return: List of company names.
    :rtype: list[str]
    """
    return [
        "ACME Corporation, S.L.",
        "Tecnologías Avanzadas S.A.",
        "CONSTRUCCIONES PÉREZ, S.L.U.",
        "María García López",
        "AYUNTAMIENTO DE MADRID",
        "Ministerio de Hacienda",
    ]
