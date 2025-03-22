from datetime import timedelta

import pytest

from expo_notifications.models import Message
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
def test_to_push_message_passes_data_through():
    message = MessageFactory(data={"key": "value"})
    push_message = message.to_push_message()
    assert push_message.data == {"key": "value"}


@pytest.mark.django_db
def test_to_push_message_converts_blank_title_to_none():
    message = MessageFactory(title="")
    push_message = message.to_push_message()
    assert push_message.title is None


@pytest.mark.django_db
def test_to_push_message_passes_title_through():
    message = MessageFactory(title="Test Title")
    push_message = message.to_push_message()
    assert push_message.title == "Test Title"


@pytest.mark.django_db
def test_to_push_message_converts_blank_body_to_none():
    message = MessageFactory(body="")
    push_message = message.to_push_message()
    assert push_message.body is None


@pytest.mark.django_db
def test_to_push_message_passes_body_through():
    message = MessageFactory(body="Test Body")
    push_message = message.to_push_message()
    assert push_message.body == "Test Body"


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


@pytest.mark.parametrize("priority", [p for p, _ in Message.PRIORITY_CHOICES])
@pytest.mark.django_db
def test_to_push_message_passes_priority_through(priority):
    message = MessageFactory(priority=priority)
    push_message = message.to_push_message()
    assert push_message.priority == priority


@pytest.mark.django_db
def test_to_push_message_converts_blank_subtitle_to_none():
    message = MessageFactory(subtitle="")
    push_message = message.to_push_message()
    assert push_message.subtitle is None


@pytest.mark.django_db
def test_to_push_message_passes_subtitle_through():
    message = MessageFactory(subtitle="Test Subtitle")
    push_message = message.to_push_message()
    assert push_message.subtitle == "Test Subtitle"


@pytest.mark.django_db
def test_to_push_message_converts_blank_sound_to_none():
    message = MessageFactory(sound="")
    push_message = message.to_push_message()
    assert push_message.sound is None


@pytest.mark.django_db
def test_to_push_message_passes_sound_through():
    message = MessageFactory(sound="default")
    push_message = message.to_push_message()
    assert push_message.sound == "default"


@pytest.mark.django_db
def test_to_push_message_converts_blank_badge_to_none():
    message = MessageFactory(badge=None)
    push_message = message.to_push_message()
    assert push_message.badge is None


@pytest.mark.parametrize("badge", [0, 1, 2, 10])
@pytest.mark.django_db
def test_to_push_message_passes_badge_through(badge):
    message = MessageFactory(badge=badge)
    push_message = message.to_push_message()
    assert push_message.badge == badge


@pytest.mark.django_db
def test_to_push_message_converts_blank_channel_id_to_none():
    message = MessageFactory(channel_id="")
    push_message = message.to_push_message()
    assert push_message.channel_id is None


@pytest.mark.django_db
def test_to_push_message_passes_channel_id_through():
    message = MessageFactory(channel_id="Default")
    push_message = message.to_push_message()
    assert push_message.channel_id == "Default"


@pytest.mark.django_db
def test_to_push_message_converts_blank_category_id_to_none():
    message = MessageFactory(category_id="")
    push_message = message.to_push_message()
    assert push_message.category is None


@pytest.mark.django_db
def test_to_push_message_passes_category_id_through():
    message = MessageFactory(category_id="Test Category")
    push_message = message.to_push_message()
    assert push_message.category == "Test Category"


@pytest.mark.parametrize("mutable_content", [True, False])
@pytest.mark.django_db
def test_to_push_message_passes_mutable_content_through(mutable_content):
    message = MessageFactory(mutable_content=mutable_content)
    push_message = message.to_push_message()
    assert push_message.mutable_content == mutable_content


@pytest.mark.django_db
def test_send_schedules_a_send_messages_task(mock_send_messages_delay_on_commit):
    message = MessageFactory()
    message.send()
    assert mock_send_messages_delay_on_commit.call_count == 1
    assert mock_send_messages_delay_on_commit.call_args.args == ([message.pk],)
