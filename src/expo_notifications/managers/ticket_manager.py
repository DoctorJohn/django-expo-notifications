from django.db import models


class TicketQueryset(models.QuerySet):
    def check_receipts(self) -> None:
        from expo_notifications.tasks import check_receipts

        ticket_pks = list(self.values_list("pk", flat=True))
        check_receipts.delay_on_commit(ticket_pks)


class TicketManager(models.Manager):
    def get_queryset(self) -> TicketQueryset:
        return TicketQueryset(self.model, using=self._db)
