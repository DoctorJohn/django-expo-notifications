from typing import TYPE_CHECKING

from django.db import models, transaction

if TYPE_CHECKING:
    from expo_notifications.models import Message  # pragma: no cover


class MessageQueryset(models.QuerySet):
    def send(self) -> None:
        from expo_notifications.tasks import send_messages

        message_pks = list(self.values_list("pk", flat=True))
        send_messages.delay_on_commit(message_pks)


class MessageManager(models.Manager):
    def get_queryset(self) -> MessageQueryset:
        return MessageQueryset(self.model, using=self._db)

    @transaction.atomic
    def send(self, **kwargs) -> "Message":
        from expo_notifications.tasks import send_messages

        message = self.create(**kwargs)
        message_pks = [message.pk]

        send_messages.delay_on_commit(message_pks)

        return message

    @transaction.atomic
    def bulk_send(self, *args, **kwargs) -> list["Message"]:
        from expo_notifications.tasks import send_messages

        messages = self.bulk_create(*args, **kwargs)
        message_pks = [message.pk for message in messages]

        send_messages.delay_on_commit(message_pks)

        return messages
