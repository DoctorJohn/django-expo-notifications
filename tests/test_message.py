from datetime import timedelta

import pytest

from tests.factories import MessageFactory


@pytest.mark.django_db
def test_str():
    message = MessageFactory()
    assert str(message) == f"Message #{message.pk}"


@pytest.mark.django_db
def test_to_push_message_sets_device_push_token_as_to():
    message = MessageFactory(device__push_token="ExponentPushToken[123]")
    push_message = message.to_push_message()
    assert push_message.to == "ExponentPushToken[123]"


@pytest.mark.django_db
def test_to_push_message_converts_blank_data_to_none():
    message = MessageFactory(data=None)
    push_message = message.to_push_message()
    assert push_message.data is None


@pytest.mark.django_db
def test_to_push_message_converts_blank_title_to_none():
    message = MessageFactory(title="")
    push_message = message.to_push_message()
    assert push_message.title is None


@pytest.mark.django_db
def test_to_push_message_converts_blank_body_to_none():
    message = MessageFactory(body="")
    push_message = message.to_push_message()
    assert push_message.body is None


@pytest.mark.django_db
def test_to_push_message_converts_blank_ttl_to_none():
    message = MessageFactory(ttl=None)
    push_message = message.to_push_message()
    assert push_message.ttl is None


@pytest.mark.parametrize(
    ("ttl_duration", "ttl_seconds"),
    [
        (timedelta(days=1), 86400),
        (timedelta(hours=1), 3600),
        (timedelta(minutes=1), 60),
    ],
)
@pytest.mark.django_db
def test_to_push_message_converts_ttl_duration_to_seconds(ttl_duration, ttl_seconds):
    message = MessageFactory(ttl=ttl_duration)
    push_message = message.to_push_message()
    assert push_message.ttl == ttl_seconds


@pytest.mark.django_db
def test_to_push_message_converts_blank_expiration_to_none():
    message = MessageFactory(expiration=None)
    push_message = message.to_push_message()
    assert push_message.expiration is None


@pytest.mark.django_db
def test_to_push_message_converts_expiration_to_unix_epoch_timestamp():
    message = MessageFactory()
    push_message = message.to_push_message()
    assert push_message.expiration == message.expiration.timestamp()


@pytest.mark.django_db
def test_to_push_message_converts_blank_priority_to_none():
    message = MessageFactory(priority="")
    push_message = message.to_push_message()
    assert push_message.priority is None


@pytest.mark.django_db
def test_to_push_message_converts_blank_subtitle_to_none():
    message = MessageFactory(subtitle="")
    push_message = message.to_push_message()
    assert push_message.subtitle is None


@pytest.mark.django_db
def test_to_push_message_converts_blank_sound_to_none():
    message = MessageFactory(sound="")
    push_message = message.to_push_message()
    assert push_message.sound is None


@pytest.mark.django_db
def test_to_push_message_converts_blank_badge_to_none():
    message = MessageFactory(badge=None)
    push_message = message.to_push_message()
    assert push_message.badge is None


@pytest.mark.django_db
def test_to_push_message_converts_blank_channel_id_to_none():
    message = MessageFactory(channel_id="")
    push_message = message.to_push_message()
    assert push_message.channel_id is None


@pytest.mark.django_db
def test_to_push_message_converts_blank_category_id_to_none():
    message = MessageFactory(category_id="")
    push_message = message.to_push_message()
    assert push_message.category is None
