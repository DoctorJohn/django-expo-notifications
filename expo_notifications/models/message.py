from django.db import models


class Message(models.Model):
    device = models.ForeignKey(
        to="expo_notifications.Device",
        on_delete=models.CASCADE,
        related_name="messages",
    )

    title = models.CharField(
        max_length=64,
    )

    body = models.CharField(
        max_length=256,
    )

    data = models.JSONField(
        blank=True,
        null=True,
    )

    ttl = models.DurationField()

    channel_id = models.CharField(
        max_length=32,
    )

    date_scheduled = models.DateTimeField()

    def __str__(self) -> str:
        return f"Message #{self.pk}"
