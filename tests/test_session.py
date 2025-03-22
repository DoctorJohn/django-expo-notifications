import sys

import pytest


@pytest.fixture(autouse=True)
def reload_module():
    for key in list(sys.modules.keys()):
        if key.startswith("expo_notifications.tasks.session"):
            del sys.modules[key]


def test_session_authorization_is_unconfigured_by_default(settings):
    settings.EXPO_NOTIFICATIONS_TOKEN = None

    from expo_notifications.tasks.session import session

    assert "Authorization" not in session.headers


def test_session_authorization_uses_the_configured_token(settings):
    settings.EXPO_NOTIFICATIONS_TOKEN = "test-token"

    from expo_notifications.tasks.session import session

    assert session.headers["Authorization"] == "Bearer test-token"
