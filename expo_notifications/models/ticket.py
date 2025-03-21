from django.db import models
from exponent_server_sdk import PushTicket


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

    def to_push_ticket(self) -> PushTicket:
        return PushTicket(
            push_message=self.message.to_push_message(),
            status=(
                PushTicket.SUCCESS_STATUS
                if self.is_success
                else PushTicket.ERROR_STATUS
            ),
            message=self.error_message or None,
            details=None,
            id=self.external_id,
        )
