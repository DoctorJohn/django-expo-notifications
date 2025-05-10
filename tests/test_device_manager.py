import pytest

from expo_notifications.models import Device

from .factories import DeviceFactory


@pytest.mark.django_db
def test_active_returns_only_active_devices():
    assert Device.objects.count() == 0

    device1 = DeviceFactory(is_active=False)
    device2 = DeviceFactory(is_active=True)

    assert not Device.objects.active.filter(pk=device1.pk).exists()
    assert Device.objects.active.filter(pk=device2.pk).exists()


@pytest.mark.django_db
def test_queryset_active_returns_only_active_devices():
    assert Device.objects.count() == 0

    device1 = DeviceFactory(is_active=False)
    device2 = DeviceFactory(is_active=True)

    assert not Device.objects.all().active.filter(pk=device1.pk).exists()
    assert Device.objects.all().active.filter(pk=device2.pk).exists()
