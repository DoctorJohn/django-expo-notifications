from datetime import timedelta

import pytest
from celery.exceptions import Retry
from exponent_server_sdk import (
    PushClient,
    PushServerError,
    PushTicket,
)
from requests.exceptions import ConnectionError, HTTPError

from expo_notifications.tasks import send_messages

from .factories import MessageFactory


@pytest.fixture
def mock_publish_multiple(mocker):
    return mocker.patch.object(PushClient, "publish_multiple")


@pytest.fixture(autouse=True)
def mock_check_receipts_apply_async(mocker):
    path = "expo_notifications.tasks.check_receipts_task.check_receipts.apply_async"
    return mocker.patch(path)


@pytest.fixture
def message1():
    return MessageFactory(device__is_active=True)


@pytest.fixture
def message2():
    return MessageFactory(device__is_active=True)


@pytest.fixture
def message3():
    return MessageFactory(device__is_active=True)


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
    assert mock_publish_multiple.call_args.args == ([message2.to_push_message()],)


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

    ticket1 = message1.tickets.get()
    assert ticket1.external_id == "test-ticket1-id"

    ticket2 = message2.tickets.get()
    assert ticket2.external_id == "test-ticket2-id"

    ticket3 = message3.tickets.get()
    assert ticket3.external_id == "test-ticket3-id"


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
    assert message1.tickets.count() == 1

    ticket1 = message1.tickets.get()
    assert ticket1.external_id == "test-push-ticket-id"
    assert ticket1.is_success == is_success


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

    ticket1 = message1.tickets.get()
    assert ticket1.is_success
    assert ticket1.external_id == "test-ticket1-id"

    ticket2 = message2.tickets.get()
    assert not ticket2.is_success
    assert ticket2.external_id == ""


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

    ticket1 = message1.tickets.get()
    assert ticket1.is_success
    assert ticket1.error_message == "test-error-message"

    ticket2 = message2.tickets.get()
    assert not ticket2.is_success
    assert ticket2.error_message == ""


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

    ticket1 = message1.tickets.get()
    assert ticket1.date_received == now


@pytest.mark.django_db
def test_schedules_check_receipts_task_for_all_success_tickets(
    mock_publish_multiple,
    mock_check_receipts_apply_async,
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

    ticket1 = message1.tickets.get()
    ticket3 = message3.tickets.get()
    assert mock_check_receipts_apply_async.call_count == 1
    assert mock_check_receipts_apply_async.call_args.kwargs["countdown"] == 60
    assert mock_check_receipts_apply_async.call_args.kwargs["kwargs"]["ticket_pks"] == [
        ticket1.pk,
        ticket3.pk,
    ]


@pytest.mark.django_db
def test_schedules_no_check_receipts_task_if_there_are_no_success_tickets(
    mock_publish_multiple,
    mock_check_receipts_apply_async,
    message1,
):
    mock_publish_multiple.return_value = [
        PushTicket(
            push_message="test-push-message",
            status=PushTicket.ERROR_STATUS,
            message="test-message",
            details=None,
            id="test-ticket1-id",
        ),
    ]

    send_messages([message1.pk])

    ticket1 = message1.tickets.get()
    assert not ticket1.is_success
    assert not mock_check_receipts_apply_async.called


@pytest.mark.django_db
def test_messages_can_be_sent_multiple_times(mock_publish_multiple, message1):
    assert message1.tickets.count() == 0

    mock_publish_multiple.side_effect = [
        [
            PushTicket(
                push_message="test-push-message",
                status=PushTicket.SUCCESS_STATUS,
                message="",
                details=None,
                id="test-ticket1-id",
            ),
        ],
        [
            PushTicket(
                push_message="test-push-message",
                status=PushTicket.SUCCESS_STATUS,
                message="",
                details=None,
                id="test-ticket2-id",
            ),
        ],
    ]

    send_messages([message1.pk])
    assert message1.tickets.count() == 1

    send_messages([message1.pk])
    assert message1.tickets.count() == 2

    ticket1 = message1.tickets.all()[0]
    assert ticket1.external_id == "test-ticket1-id"

    ticket2 = message1.tickets.all()[1]
    assert ticket2.external_id == "test-ticket2-id"
