import requests
from celery import shared_task
from django.utils import timezone
from exponent_server_sdk import (
    DeviceNotRegisteredError,
    PushClient,
    PushServerError,
    PushTicket,
    PushTicketError,
)
from requests.exceptions import ConnectionError, HTTPError

from expo_notifications.conf import settings
from expo_notifications.models import Message, Ticket
from expo_notifications.tasks import check_receipts

session = requests.Session()
session.headers.update(
    {
        "accept": "application/json",
        "accept-encoding": "gzip, deflate",
        "content-type": "application/json",
    }
)

if settings.token is not None:
    session.headers.update({"Authorization": f"Bearer {settings.token}"})


@shared_task(
    bind=True,
    ignore_result=True,
    max_retries=settings.sending_task_max_retries,
    default_retry_delay=settings.sending_task_retry_delay.total_seconds(),
)
def send_messages(self, message_pks: list[str]) -> None:
    messages = Message.objects.filter(pk__in=message_pks, device__is_active=True)

    push_messages = [message.to_push_message() for message in messages]

    push_client = PushClient(session=session)

    try:
        push_tickets: list[PushTicket] = push_client.publish_multiple(push_messages)
    except PushServerError:
        raise self.retry()
    except (ConnectionError, HTTPError):
        raise self.retry()

    tickets: list[Ticket] = []

    for message, push_ticket in zip(messages, push_tickets):
        try:
            push_ticket.validate_response()
        except DeviceNotRegisteredError:
            message.device.is_active = False
            message.device.save()
        except PushTicketError:
            pass

        tickets.append(
            Ticket(
                message=message,
                is_success=push_ticket.is_success(),
                external_id=push_ticket.id,
                error_message=push_ticket.message,
                date_received=timezone.now(),
            )
        )

    pks_of_success_tickets = [
        ticket.pk for ticket in Ticket.objects.bulk_create(tickets) if ticket.is_success
    ]

    check_receipts.apply_async(
        kwargs={"ticket_pks": pks_of_success_tickets},
        countdown=settings.receipt_check_delay.total_seconds(),
    )
