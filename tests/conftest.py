"""Независимые данные для каждого теста."""

from pathlib import Path

import pytest

from sportpartner.storage import load_data


@pytest.fixture
def data() -> dict:
    """Загрузить отдельную копию демонстрационных данных."""
    return load_data(Path(__file__).parents[1] / "data" / "store.json")
