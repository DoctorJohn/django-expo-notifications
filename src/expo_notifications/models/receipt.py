from django.db import models


class Receipt(models.Model):
    ticket = models.ForeignKey(
        to="expo_notifications.Ticket",
        on_delete=models.CASCADE,
        related_name="receipts",
    )

    is_success = models.BooleanField()

    error_message = models.TextField(
        blank=True,
    )

    date_checked = models.DateTimeField()

    def __str__(self) -> str:
        return f"Receipt #{self.pk}"
