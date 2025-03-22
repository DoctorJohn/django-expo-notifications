import pytest
from bs4 import BeautifulSoup
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME
from django.contrib.messages import get_messages
from django.urls import reverse

from tests.factories import ReceiptFactory, TicketFactory

CHANGELIST_URL = reverse("admin:expo_notifications_ticket_changelist")


def trigger_check_tickets_action(client, ticket_pks):
    data = {"action": "check_tickets", ACTION_CHECKBOX_NAME: ticket_pks}
    return client.post(CHANGELIST_URL, data)


@pytest.mark.django_db
def test_changelist_renders_correctly(admin_client):
    ticket1 = TicketFactory()
    ticket2 = TicketFactory()
    ReceiptFactory.create_batch(3, ticket=ticket2)

    response = admin_client.get(CHANGELIST_URL)
    assert response.status_code == 200

    soup = BeautifulSoup(response.content, "html.parser")
    str_a_tags = soup.select(".field-__str__ a")
    receipt_link_tags = soup.select(".field-receipts_link")

    str_td1 = str_a_tags[0]
    assert str_td1
    assert str_td1.text == str(ticket2)

    str_td2 = str_a_tags[1]
    assert str_td2
    assert str_td2.text == str(ticket1)

    receipt_link_td1 = receipt_link_tags[0]
    assert receipt_link_td1
    assert receipt_link_td1.text == "3"

    receipt_link_td2 = receipt_link_tags[1]
    assert receipt_link_td2
    assert receipt_link_td2.text == "0"


@pytest.mark.django_db
def test_check_tickets_action_schedules_a_check_tickets_task(
    admin_client, mock_check_receipts_delay_on_commit
):
    ticket1 = TicketFactory()
    ticket2 = TicketFactory()

    response = trigger_check_tickets_action(admin_client, [ticket1.pk, ticket2.pk])
    assert response.status_code == 302
    assert response.url == "/admin/expo_notifications/ticket/"

    assert mock_check_receipts_delay_on_commit.call_count == 1
    assert mock_check_receipts_delay_on_commit.call_args.args == (
        [ticket2.pk, ticket1.pk],
    )


@pytest.mark.parametrize(
    ("ticket_count", "admin_message"),
    [
        (1, "1 ticket receipt will be checked."),
        (2, "2 ticket receipts will be checked."),
        (30, "30 ticket receipts will be checked."),
    ],
)
@pytest.mark.django_db
def test_check_tickets_action_reports_how_many_ticket_receipts_will_be_checked(
    admin_client, ticket_count, admin_message
):
    tickets = TicketFactory.create_batch(ticket_count)
    ticket_pks = [ticket.pk for ticket in tickets]

    response = trigger_check_tickets_action(admin_client, ticket_pks)
    assert response.status_code == 302
    assert response.url == "/admin/expo_notifications/ticket/"

    admin_messages = [m.message for m in get_messages(response.wsgi_request)]
    assert len(admin_messages) == 1
    assert admin_messages[0] == admin_message
