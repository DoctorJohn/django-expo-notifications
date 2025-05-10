import pytest
from bs4 import BeautifulSoup
from django.urls import reverse

from .factories import DeviceFactory, MessageFactory

CHANGELIST_URL = reverse("admin:expo_notifications_device_changelist")


@pytest.mark.django_db
def test_changelist_renders_correctly(admin_client):
    device1 = DeviceFactory()
    device2 = DeviceFactory()
    MessageFactory.create_batch(3, device=device2)

    response = admin_client.get(CHANGELIST_URL)
    assert response.status_code == 200

    soup = BeautifulSoup(response.content, "html.parser")
    str_a_tags = soup.select(".field-__str__ a")
    messages_link_tags = soup.select(".field-messages_link")

    str_td1 = str_a_tags[0]
    assert str_td1
    assert str_td1.text == str(device2)

    str_td2 = str_a_tags[1]
    assert str_td2
    assert str_td2.text == str(device1)

    messages_link_td1 = messages_link_tags[0]
    assert messages_link_td1
    assert messages_link_td1.text == "3"

    messages_link_td2 = messages_link_tags[1]
    assert messages_link_td2
    assert messages_link_td2.text == "0"
