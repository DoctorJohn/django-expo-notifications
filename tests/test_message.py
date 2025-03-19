import pytest

from tests.factories import MessageFactory


@pytest.mark.django_db
def test_str():
    message = MessageFactory()
    assert str(message) == f"Message #{message.pk}"
