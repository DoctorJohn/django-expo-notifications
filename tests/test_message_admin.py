import pytest
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.contrib.messages import get_messages
from django.urls import reverse

from tests.factories import MessageFactory

CHANGELIST_URL = reverse("admin:expo_notifications_message_changelist")


def trigger_send_messages_action(client, message_pks):
    data = {"action": "send_messages", ACTION_CHECKBOX_NAME: message_pks}
    return client.post(CHANGELIST_URL, data)


@pytest.fixture(autouse=True)
def mock_send_messages_delay_on_commit(mocker):
    path = "expo_notifications.tasks.send_messages_task.send_messages.delay_on_commit"
    return mocker.patch(path)


@pytest.mark.django_db
def test_send_messages_action_schedules_a_send_messages_task(
    admin_client, mock_send_messages_delay_on_commit
):
    message1 = MessageFactory.create()
    message2 = MessageFactory.create()

    response = trigger_send_messages_action(admin_client, [message1.pk, message2.pk])
    assert response.status_code == 302
    assert response.url == "/admin/expo_notifications/message/"

    assert mock_send_messages_delay_on_commit.call_count == 1
    assert mock_send_messages_delay_on_commit.call_args.args == (
        [message2.pk, message1.pk],
    )


@pytest.mark.parametrize(
    ("message_count", "admin_message"),
    [
        (1, "1 message was sent."),
        (2, "2 messages were sent."),
        (30, "30 messages were sent."),
    ],
)
@pytest.mark.django_db
def test_send_messages_action_reports_how_many_messages_were_sent(
    admin_client, message_count, admin_message
):
    messages = MessageFactory.create_batch(message_count)
    message_pks = [message.pk for message in messages]

    response = trigger_send_messages_action(admin_client, message_pks)
    assert response.status_code == 302
    assert response.url == "/admin/expo_notifications/message/"

    admin_messages = [m.message for m in get_messages(response.wsgi_request)]
    assert len(admin_messages) == 1
    assert admin_messages[0] == admin_message
