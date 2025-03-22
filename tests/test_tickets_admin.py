import pytest
from bs4 import BeautifulSoup
from django.urls import reverse

from tests.factories import ReceiptFactory, TicketFactory

CHANGELIST_URL = reverse("admin:expo_notifications_ticket_changelist")


@pytest.mark.django_db
def test_changelist_renders_correctly(admin_client):
    ticket1 = TicketFactory()
    ticket2 = TicketFactory()
    receipt = ReceiptFactory(ticket=ticket2)

    response = admin_client.get(CHANGELIST_URL)
    assert response.status_code == 200

    soup = BeautifulSoup(response.content, "html.parser")
    str_a_tags = soup.select(".field-__str__ a")
    receipt_link_tags = soup.select(".field-receipt_link")

    str_td1 = str_a_tags[0]
    assert str_td1
    assert str_td1.text == str(ticket2)

    str_td2 = str_a_tags[1]
    assert str_td2
    assert str_td2.text == str(ticket1)

    messages_link_td1 = receipt_link_tags[0]
    assert messages_link_td1
    assert messages_link_td1.text == str(receipt)

    messages_link_td2 = receipt_link_tags[1]
    assert messages_link_td2
    assert messages_link_td2.text == "-"
