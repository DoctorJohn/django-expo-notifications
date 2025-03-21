import pytest

from expo_notifications.models import Message
from tests.factories import DeviceFactory, MessageFactory


@pytest.fixture(autouse=True)
def mock_send_messages_delay_on_commit(mocker):
    path = "expo_notifications.tasks.send_messages_task.send_messages.delay_on_commit"
    return mocker.patch(path)


@pytest.mark.django_db
def test_send_creates_message():
    device = DeviceFactory()
    assert device.messages.count() == 0

    message_data = MessageFactory.build(device=device).__dict__.copy()
    message_data.pop("_state")

    Message.objects.send(**message_data)
    assert device.messages.count() == 1

    message = device.messages.first()
    assert message.to_push_message() == message.to_push_message()


@pytest.mark.django_db
def test_send_delays_message_on_commit(mock_send_messages_delay_on_commit):
    device = DeviceFactory()

    message_data = MessageFactory.build(device=device).__dict__.copy()
    message_data.pop("_state")

    Message.objects.send(**message_data)
    message = device.messages.first()

    assert mock_send_messages_delay_on_commit.call_count == 1
    assert mock_send_messages_delay_on_commit.call_args.args == ([message.pk],)


@pytest.mark.django_db
def test_bulk_send_creates_messages():
    device = DeviceFactory()
    assert device.messages.count() == 0

    unsaved_message1 = MessageFactory.build(device=device)
    unsaved_message2 = MessageFactory.build(device=device)

    Message.objects.bulk_send([unsaved_message1, unsaved_message2])
    assert device.messages.count() == 2

    message1 = device.messages.first()
    assert message1.to_push_message() == unsaved_message1.to_push_message()

    message2 = device.messages.last()
    assert message2.to_push_message() == unsaved_message2.to_push_message()


@pytest.mark.django_db
def test_bulk_send_delays_messages_on_commit(mock_send_messages_delay_on_commit):
    device = DeviceFactory()

    Message.objects.bulk_send(
        [
            MessageFactory.build(device=device),
            MessageFactory.build(device=device),
        ]
    )

    message1 = device.messages.first()
    message2 = device.messages.last()

    assert mock_send_messages_delay_on_commit.call_count == 1
    assert mock_send_messages_delay_on_commit.call_args.args == (
        [message1.pk, message2.pk],
    )
