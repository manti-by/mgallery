from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_redis_client() -> MagicMock:
    client = MagicMock()
    client.get.return_value = None
    client.keys.return_value = []
    return client
