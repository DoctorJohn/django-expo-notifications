from django.db import models


class Ticket(models.Model):
    message = models.OneToOneField(
        to="expo_notifications.Message",
        on_delete=models.CASCADE,
        related_name="ticket",
    )

    is_success = models.BooleanField()

    external_id = models.CharField(
        max_length=64,
        blank=True,
    )

    error_message = models.TextField(
        blank=True,
    )

    date_received = models.DateTimeField()

    def __str__(self) -> str:
        return f"Ticket #{self.pk}"
