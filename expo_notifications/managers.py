from typing import TYPE_CHECKING

from django.db import models

if TYPE_CHECKING:
    from expo_notifications.models import Message  # pragma: no cover


class MessageManager(models.Manager):
    def send(self, **kwargs) -> "Message":
        from expo_notifications.tasks import send_messages

        message = self.create(**kwargs)
        message_pks = [message.pk]

        send_messages.delay_on_commit(message_pks)

        return message

    def bulk_send(self, *args, **kwargs) -> list["Message"]:
        from expo_notifications.tasks import send_messages

        messages = self.bulk_create(*args, **kwargs)
        message_pks = [message.pk for message in messages]

        send_messages.delay_on_commit(message_pks)

        return messages
