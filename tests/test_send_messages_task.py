from datetime import timedelta

import pytest
from celery.exceptions import Retry
from exponent_server_sdk import (
    PushClient,
    PushMessage,
    PushServerError,
    PushTicket,
)
from requests.exceptions import ConnectionError, HTTPError

from expo_notifications.tasks import send_messages
from tests.factories import MessageFactory


@pytest.fixture
def mock_publish_multiple(mocker):
    return mocker.patch.object(PushClient, "publish_multiple")


@pytest.fixture(autouse=True)
def mock_check_receipts_task(mocker):
    path = "expo_notifications.tasks.check_receipts_task.check_receipts.apply_async"
    return mocker.patch(path)


@pytest.fixture
def message1():
    return MessageFactory.create(device__is_active=True)


@pytest.fixture
def message2():
    return MessageFactory.create(device__is_active=True)


@pytest.fixture
def message3():
    return MessageFactory.create(device__is_active=True)


@pytest.mark.django_db
def test_retries_on_push_server_errors(mock_publish_multiple, message1, message2):
    mock_publish_multiple.side_effect = PushServerError("Invalid server response", None)

    with pytest.raises(Retry):
        send_messages([message1.pk, message2.pk])


@pytest.mark.django_db
def test_retries_on_connection_errors(mock_publish_multiple, message1, message2):
    mock_publish_multiple.side_effect = ConnectionError()

    with pytest.raises(Retry):
        send_messages([message1.pk, message2.pk])


@pytest.mark.django_db
def test_retries_on_http_errors(mock_publish_multiple, message1, message2):
    mock_publish_multiple.side_effect = HTTPError()

    with pytest.raises(Retry):
        send_messages([message1.pk, message2.pk])


@pytest.mark.django_db
def test_sends_push_messages_only_for_messages_with_active_devices(
    mock_publish_multiple, message1, message2
):
    message1.device.is_active = False
    message1.device.save()

    send_messages([message1.pk, message2.pk])

    assert mock_publish_multiple.call_count == 1
    assert mock_publish_multiple.call_args.args == (
        [
            PushMessage(
                to=message2.device.push_token,
                title=message2.title,
                body=message2.body,
                data=message2.data,
                sound=None,
                ttl=int(message2.ttl.total_seconds()),
                expiration=None,
                priority=None,
                badge=None,
                category=None,
                display_in_foreground=None,
                channel_id=message2.channel_id,
                subtitle=None,
                mutable_content=None,
            )
        ],
    )


@pytest.mark.django_db
def test_deactivates_unknown_devices(mock_publish_multiple, message1, message2):
    mock_publish_multiple.return_value = [
        PushTicket(
            push_message="test-push-message",
            status=PushTicket.SUCCESS_STATUS,
            message="",
            details=None,
            id="test-ticket1-id",
        ),
        PushTicket(
            push_message="test-push-message",
            status=PushTicket.ERROR_STATUS,
            message="test-message",
            details={"error": PushTicket.ERROR_DEVICE_NOT_REGISTERED},
            id="test-ticket2-id",
        ),
    ]

    assert message1.device.is_active
    assert message2.device.is_active

    send_messages([message1.pk, message2.pk])

    message1.refresh_from_db()
    assert message1.device.is_active

    message2.refresh_from_db()
    assert not message2.device.is_active


@pytest.mark.parametrize(
    "details",
    [
        None,
        {"error": PushTicket.ERROR_DEVICE_NOT_REGISTERED},
        {"error": PushTicket.ERROR_MESSAGE_TOO_BIG},
        {"error": PushTicket.ERROR_MESSAGE_RATE_EXCEEDED},
    ],
)
@pytest.mark.django_db
def test_stores_push_tickets_for_all_messages(
    mock_publish_multiple, message1, message2, message3, details
):
    mock_publish_multiple.return_value = [
        PushTicket(
            push_message="test-push-message",
            status=PushTicket.SUCCESS_STATUS,
            message="",
            details=None,
            id="test-ticket1-id",
        ),
        PushTicket(
            push_message="test-push-message",
            status=PushTicket.ERROR_STATUS,
            message="test-message",
            details=details,
            id="test-ticket2-id",
        ),
        PushTicket(
            push_message="test-push-message",
            status=PushTicket.SUCCESS_STATUS,
            message="",
            details=None,
            id="test-ticket3-id",
        ),
    ]

    send_messages([message1.pk, message2.pk, message3.pk])

    message1.refresh_from_db()
    assert message1.ticket
    assert message1.ticket.external_id == "test-ticket1-id"

    message2.refresh_from_db()
    assert message2.ticket
    assert message2.ticket.external_id == "test-ticket2-id"

    message3.refresh_from_db()
    assert message3.ticket
    assert message3.ticket.external_id == "test-ticket3-id"


@pytest.mark.parametrize(
    ("status", "is_success"),
    [
        (PushTicket.SUCCESS_STATUS, True),
        (PushTicket.ERROR_STATUS, False),
    ],
)
@pytest.mark.django_db
def test_stores_push_ticket_status(mock_publish_multiple, message1, status, is_success):
    mock_publish_multiple.return_value = [
        PushTicket(
            push_message="test-push-message",
            status=status,
            message="",
            details=None,
            id="test-push-ticket-id",
        )
    ]

    send_messages([message1.pk])
    assert message1.ticket
    assert message1.ticket.external_id == "test-push-ticket-id"
    assert message1.ticket.is_success == is_success


@pytest.mark.django_db
def test_stores_push_ticket_external_id(mock_publish_multiple, message1, message2):
    mock_publish_multiple.return_value = [
        PushTicket(
            push_message="test-push-message",
            status=PushTicket.SUCCESS_STATUS,
            message="",
            details=None,
            id="test-ticket1-id",
        ),
        PushTicket(
            push_message="test-push-message",
            status=PushTicket.ERROR_STATUS,
            message="test-error-message",
            details=None,
            id="",
        ),
    ]

    send_messages([message1.pk, message2.pk])
    assert message1.ticket.is_success
    assert message1.ticket.external_id == "test-ticket1-id"
    assert not message2.ticket.is_success
    assert message2.ticket.external_id == ""


@pytest.mark.django_db
def test_stores_push_ticket_error_message(mock_publish_multiple, message1, message2):
    mock_publish_multiple.return_value = [
        PushTicket(
            push_message="test-push-message",
            status=PushTicket.SUCCESS_STATUS,
            message="test-error-message",
            details=None,
            id="test-ticket1-id",
        ),
        PushTicket(
            push_message="test-push-message",
            status=PushTicket.ERROR_STATUS,
            message="",
            details=None,
            id="",
        ),
    ]

    send_messages([message1.pk, message2.pk])
    assert message1.ticket
    assert message1.ticket.is_success
    assert message1.ticket.error_message == "test-error-message"
    assert message2.ticket
    assert not message2.ticket.is_success
    assert message2.ticket.error_message == ""


@pytest.mark.parametrize(
    "status",
    [
        PushTicket.SUCCESS_STATUS,
        PushTicket.ERROR_STATUS,
    ],
)
@pytest.mark.django_db
def test_stores_push_ticket_receival_date(mock_publish_multiple, message1, now, status):
    mock_publish_multiple.return_value = [
        PushTicket(
            push_message="test-push-message",
            status=status,
            message="",
            details=None,
            id="test-push-ticket-id",
        )
    ]

    send_messages([message1.pk])
    assert message1.ticket
    assert message1.ticket.date_received == now


@pytest.mark.django_db
def test_schedules_check_receipts_tasks_for_all_success_tickets(
    mock_publish_multiple,
    mock_check_receipts_task,
    settings,
    message1,
    message2,
    message3,
):
    settings.EXPO_NOTIFICATIONS_RECEIPT_CHECK_DELAY = timedelta(seconds=60)

    mock_publish_multiple.return_value = [
        PushTicket(
            push_message="test-push-message",
            status=PushTicket.SUCCESS_STATUS,
            message="",
            details=None,
            id="test-ticket1-id",
        ),
        PushTicket(
            push_message="test-push-message",
            status=PushTicket.ERROR_STATUS,
            message="test-message",
            details=None,
            id="test-ticket2-id",
        ),
        PushTicket(
            push_message="test-push-message",
            status=PushTicket.SUCCESS_STATUS,
            message="",
            details=None,
            id="test-ticket3-id",
        ),
    ]

    send_messages([message1.pk, message2.pk, message3.pk])

    assert mock_check_receipts_task.call_count == 1
    assert mock_check_receipts_task.call_args.kwargs["countdown"] == 60
    assert mock_check_receipts_task.call_args.kwargs["kwargs"]["ticket_pks"] == [
        message1.ticket.pk,
        message3.ticket.pk,
    ]
