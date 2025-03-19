from django.db import models
from django.conf import settings


class Device(models.Model):
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="devices",
    )

    lang = models.CharField(
        # e.g. for ISO 639-1 set 1 & ISO 3166-1 alpha-2
        max_length=5,
    )

    push_token = models.CharField(
        # https://github.com/expo/expo/issues/1135#issuecomment-399622890
        max_length=4096,
    )

    date_registered = models.DateTimeField()

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        unique_together = (
            "user",
            "push_token",
        )

    def __str__(self) -> str:
        return f"Device #{self.pk} of {self.user.username}"
