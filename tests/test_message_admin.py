import pytest
from bs4 import BeautifulSoup
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.contrib.messages import get_messages
from django.urls import reverse

from tests.factories import MessageFactory, TicketFactory

CHANGELIST_URL = reverse("admin:expo_notifications_message_changelist")


def trigger_send_messages_action(client, message_pks):
    data = {"action": "send_messages", ACTION_CHECKBOX_NAME: message_pks}
    return client.post(CHANGELIST_URL, data)


@pytest.mark.django_db
def test_changelist_renders_correctly(admin_client):
    message1 = MessageFactory()
    message2 = MessageFactory()
    TicketFactory.create_batch(3, message=message2)

    response = admin_client.get(CHANGELIST_URL)
    assert response.status_code == 200

    soup = BeautifulSoup(response.content, "html.parser")
    str_a_tags = soup.select(".field-__str__ a")
    tickets_link_tags = soup.select(".field-tickets_link")

    str_td1 = str_a_tags[0]
    assert str_td1
    assert str_td1.text == str(message2)

    str_td2 = str_a_tags[1]
    assert str_td2
    assert str_td2.text == str(message1)

    ticket_link_td1 = tickets_link_tags[0]
    assert ticket_link_td1
    assert ticket_link_td1.text == "3"

    ticket_link_td2 = tickets_link_tags[1]
    assert ticket_link_td2
    assert ticket_link_td2.text == "0"


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
