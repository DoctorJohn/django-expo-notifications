from django.db import models
from django.utils import timezone
from exponent_server_sdk import PushMessage

from expo_notifications.managers import MessageManager


class Message(models.Model):
    objects = MessageManager()

    device = models.ForeignKey(
        to="expo_notifications.Device",
        on_delete=models.CASCADE,
        related_name="messages",
    )

    data = models.JSONField(
        blank=True,
        null=True,
    )

    title = models.CharField(
        max_length=64,
        blank=True,
    )

    body = models.CharField(
        max_length=256,
        blank=True,
    )

    ttl = models.DurationField(
        blank=True,
        null=True,
    )

    expiration = models.DateTimeField(
        blank=True,
        null=True,
    )

    PRIORITY_DEFAULT = "default"
    PRIORITY_NORMAL = "normal"
    PRIORITY_HIGH = "high"
    PRIORITY_CHOICES = (
        (PRIORITY_DEFAULT, "Default"),
        (PRIORITY_NORMAL, "Normal"),
        (PRIORITY_HIGH, "High"),
    )

    priority = models.CharField(
        max_length=7,
        blank=True,
        null=True,
        choices=PRIORITY_CHOICES,
    )

    subtitle = models.CharField(
        max_length=64,
        blank=True,
    )

    sound = models.CharField(
        max_length=64,
        blank=True,
    )

    badge = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
    )

    channel_id = models.CharField(
        max_length=32,
        blank=True,
    )

    category_id = models.CharField(
        max_length=64,
        blank=True,
    )

    mutable_content = models.BooleanField(
        default=False,
    )

    date_created = models.DateTimeField(
        default=timezone.now,
    )

    def __str__(self) -> str:
        return f"Message #{self.pk}"

    def to_push_message(self) -> PushMessage:
        return PushMessage(
            to=self.device.push_token,
            data=self.data,
            title=self.title or None,
            body=self.body or None,
            sound=self.sound or None,
            ttl=self.ttl.total_seconds() if self.ttl else None,
            expiration=self.expiration.timestamp() if self.expiration else None,
            priority=self.priority or None,
            badge=self.badge,
            category=self.category_id or None,
            display_in_foreground=None,
            channel_id=self.channel_id or None,
            subtitle=self.subtitle or None,
            mutable_content=self.mutable_content,
        )
