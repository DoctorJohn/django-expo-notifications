from datetime import datetime, timezone

import pytest


@pytest.fixture
def now(mocker):
    now_value = datetime.now(timezone.utc)
    mock_now = mocker.patch("django.utils.timezone.now")
    mock_now.return_value = now_value
    return now_value


@pytest.fixture(autouse=True)
def mock_send_messages_delay_on_commit(mocker):
    path = "expo_notifications.tasks.send_messages_task.send_messages.delay_on_commit"
    return mocker.patch(path)
