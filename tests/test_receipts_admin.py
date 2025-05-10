import pytest
from bs4 import BeautifulSoup
from django.urls import reverse

from .factories import ReceiptFactory

CHANGELIST_URL = reverse("admin:expo_notifications_receipt_changelist")


@pytest.mark.django_db
def test_changelist_renders_correctly(admin_client):
    receipt1 = ReceiptFactory()
    receipt2 = ReceiptFactory()

    response = admin_client.get(CHANGELIST_URL)
    assert response.status_code == 200

    soup = BeautifulSoup(response.content, "html.parser")
    str_a_tags = soup.select(".field-__str__ a")

    str_td1 = str_a_tags[0]
    assert str_td1
    assert str_td1.text == str(receipt2)

    str_td2 = str_a_tags[1]
    assert str_td2
    assert str_td2.text == str(receipt1)
