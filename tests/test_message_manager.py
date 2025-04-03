import pytest

from expo_notifications.models import Message
from tests.factories import DeviceFactory, MessageFactory


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
def test_send_schedules_a_send_messages_task(mock_send_messages_delay_on_commit):
    device = DeviceFactory()

    message_data = MessageFactory.build(device=device).__dict__.copy()
    message_data.pop("_state")

    Message.objects.send(**message_data)
    message = device.messages.first()

    assert mock_send_messages_delay_on_commit.call_count == 1
    assert mock_send_messages_delay_on_commit.call_args.args == ([message.pk],)


@pytest.mark.django_db
def test_send_rolls_back_when_sending_fails(mock_send_messages_delay_on_commit):
    device = DeviceFactory()
    assert device.messages.count() == 0

    message_data = MessageFactory.build(device=device).__dict__.copy()
    message_data.pop("_state")

    mock_send_messages_delay_on_commit.side_effect = Exception("Something went wrong")

    with pytest.raises(Exception, match="Something went wrong"):
        Message.objects.send(**message_data)

    assert device.messages.count() == 0


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
def test_bulk_send_schedules_no_send_messages_task_if_there_are_no_messages(
    mock_send_messages_delay_on_commit,
):
    Message.objects.bulk_send([])

    assert not mock_send_messages_delay_on_commit.called


@pytest.mark.django_db
def test_bulk_send_schedules_a_send_messages_task(mock_send_messages_delay_on_commit):
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


@pytest.mark.django_db
def test_bulk_send_rolls_back_when_sending_fails(mock_send_messages_delay_on_commit):
    device = DeviceFactory()
    assert device.messages.count() == 0

    mock_send_messages_delay_on_commit.side_effect = Exception("Something went wrong")

    with pytest.raises(Exception, match="Something went wrong"):
        Message.objects.bulk_send(
            [
                MessageFactory.build(device=device),
                MessageFactory.build(device=device),
            ]
        )

    assert device.messages.count() == 0


@pytest.mark.django_db
def test_queryset_send_schedules_no_send_messages_task_for_empty_querysets(
    mock_send_messages_delay_on_commit,
):
    assert Message.objects.count() == 0

    Message.objects.none().send()
    assert not mock_send_messages_delay_on_commit.called


@pytest.mark.django_db
def test_queryset_send_schedules_a_send_messages_task(
    mock_send_messages_delay_on_commit,
):
    assert Message.objects.count() == 0

    message1 = MessageFactory()
    message2 = MessageFactory()

    Message.objects.all().send()

    assert mock_send_messages_delay_on_commit.call_count == 1
    assert mock_send_messages_delay_on_commit.call_args.args == (
        [message1.pk, message2.pk],
    )
