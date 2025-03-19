from datetime import datetime, timezone

import pytest


@pytest.fixture
def now(mocker):
    now_value = datetime.now(timezone.utc)
    mock_now = mocker.patch("django.utils.timezone.now")
    mock_now.return_value = now_value
    return now_value
