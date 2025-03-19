import pytest
from tests.factories import DeviceFactory


@pytest.mark.django_db
def test_str():
    device = DeviceFactory()
    assert str(device) == f"Device #{device.pk} of {device.user.username}"
