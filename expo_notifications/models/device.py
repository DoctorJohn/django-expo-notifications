from django.conf import settings
from django.db import models
from django.utils import timezone

from expo_notifications.managers import DeviceManager


class Device(models.Model):
    objects = DeviceManager()

    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="devices",
    )

    lang = models.CharField(
        # e.g. for ISO 639-1 & ISO 3166-1 alpha-2
        max_length=5,
        blank=True,
    )

    push_token = models.CharField(
        # https://github.com/expo/expo/issues/1135#issuecomment-399622890
        max_length=4096,
    )

    date_registered = models.DateTimeField(
        default=timezone.now,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        unique_together = (
            "user",
            "push_token",
        )

    def __str__(self) -> str:
        return f"Device #{self.pk} of {self.user}"
