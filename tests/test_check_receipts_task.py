import pytest
from celery.exceptions import Retry
from exponent_server_sdk import (
    PushClient,
    PushReceipt,
    PushServerError,
)
from requests.exceptions import ConnectionError, HTTPError

from expo_notifications.tasks import check_receipts
from tests.factories import TicketFactory


@pytest.fixture
def mock_check_receipts_multiple(mocker):
    return mocker.patch.object(PushClient, "check_receipts_multiple")


@pytest.fixture
def ticket1():
    return TicketFactory(external_id="test-id-1")


@pytest.fixture
def ticket2():
    return TicketFactory(external_id="test-id-2")


@pytest.mark.django_db
def test_retries_on_push_server_errors(mock_check_receipts_multiple, ticket1, ticket2):
    mock_check_receipts_multiple.side_effect = PushServerError(
        "Invalid server response", None
    )

    with pytest.raises(Retry):
        check_receipts([ticket1.pk, ticket2.pk])


@pytest.mark.django_db
def test_retries_on_connection_errors(mock_check_receipts_multiple, ticket1, ticket2):
    mock_check_receipts_multiple.side_effect = ConnectionError()

    with pytest.raises(Retry):
        check_receipts([ticket1.pk, ticket2.pk])


@pytest.mark.django_db
def test_retries_on_http_errors(mock_check_receipts_multiple, ticket1, ticket2):
    mock_check_receipts_multiple.side_effect = HTTPError()

    with pytest.raises(Retry):
        check_receipts([ticket1.pk, ticket2.pk])


@pytest.mark.django_db
def test_skips_tickets_without_external_id(
    mock_check_receipts_multiple, ticket1, ticket2
):
    ticket1.external_id = ""
    ticket1.save()

    check_receipts([ticket1.pk, ticket2.pk])
    assert mock_check_receipts_multiple.call_count == 1
    assert mock_check_receipts_multiple.call_args.args == ([ticket2.to_push_ticket()],)


@pytest.mark.django_db
def test_calls_check_receipts_multiple_with_expected_params(
    mock_check_receipts_multiple, ticket1, ticket2
):
    push_tickets = [
        ticket1.to_push_ticket(),
        ticket2.to_push_ticket(),
    ]

    check_receipts([ticket1.pk, ticket2.pk])
    assert mock_check_receipts_multiple.call_count == 1
    assert mock_check_receipts_multiple.call_args.args == (push_tickets,)


@pytest.mark.django_db
def test_deactivates_unknown_devices(mock_check_receipts_multiple, ticket1):
    assert ticket1.receipts.count() == 0

    device = ticket1.message.device
    device.is_active = True
    device.save()
    assert device.is_active

    mock_check_receipts_multiple.return_value = [
        PushReceipt(
            id=ticket1.external_id,
            status=PushReceipt.ERROR_STATUS,
            message="",
            details={"error": PushReceipt.ERROR_DEVICE_NOT_REGISTERED},
        )
    ]

    check_receipts([ticket1.pk])
    assert ticket1.receipts.count() == 1

    device.refresh_from_db()
    assert not device.is_active


@pytest.mark.parametrize(
    "details",
    [
        None,
        {"error": PushReceipt.ERROR_DEVICE_NOT_REGISTERED},
        {"error": PushReceipt.ERROR_MESSAGE_TOO_BIG},
        {"error": PushReceipt.ERROR_MESSAGE_RATE_EXCEEDED},
    ],
)
@pytest.mark.django_db
def test_stores_receipts_for_all_tickets(
    mock_check_receipts_multiple, ticket1, ticket2, details
):
    assert ticket1.receipts.count() == 0
    assert ticket2.receipts.count() == 0

    mock_check_receipts_multiple.return_value = [
        PushReceipt(
            id=ticket1.external_id,
            status=PushReceipt.ERROR_STATUS,
            message="",
            details=details,
        ),
        PushReceipt(
            id=ticket2.external_id,
            status=PushReceipt.SUCCESS_STATUS,
            message="",
            details=None,
        ),
    ]

    check_receipts([ticket1.pk, ticket2.pk])

    receipt1 = ticket1.receipts.get()
    assert not receipt1.is_success

    receipt2 = ticket2.receipts.get()
    assert receipt2.is_success


@pytest.mark.parametrize(
    ("status", "is_success"),
    [
        (PushReceipt.SUCCESS_STATUS, True),
        (PushReceipt.ERROR_STATUS, False),
    ],
)
@pytest.mark.django_db
def test_stores_push_receipt_status(
    mock_check_receipts_multiple, ticket1, status, is_success
):
    mock_check_receipts_multiple.return_value = [
        PushReceipt(
            id=ticket1.external_id,
            status=status,
            message="",
            details=None,
        ),
    ]

    check_receipts([ticket1.pk])

    receipt1 = ticket1.receipts.get()
    assert receipt1.is_success == is_success


@pytest.mark.parametrize(
    "details",
    [
        None,
        {"error": PushReceipt.ERROR_DEVICE_NOT_REGISTERED},
        {"error": PushReceipt.ERROR_MESSAGE_TOO_BIG},
        {"error": PushReceipt.ERROR_MESSAGE_RATE_EXCEEDED},
    ],
)
@pytest.mark.django_db
def test_stores_push_ticket_error_message(
    mock_check_receipts_multiple, ticket1, ticket2, details
):
    mock_check_receipts_multiple.return_value = [
        PushReceipt(
            id=ticket1.external_id,
            status=PushReceipt.ERROR_STATUS,
            message="test-error-message",
            details=details,
        ),
        PushReceipt(
            id=ticket2.external_id,
            status=PushReceipt.SUCCESS_STATUS,
            message="",
            details=None,
        ),
    ]

    check_receipts([ticket1.pk, ticket2.pk])

    receipt1 = ticket1.receipts.get()
    assert not receipt1.is_success
    assert receipt1.error_message == "test-error-message"

    receipt2 = ticket2.receipts.get()
    assert receipt2.is_success
    assert receipt2.error_message == ""


@pytest.mark.parametrize(
    "status",
    [
        PushReceipt.SUCCESS_STATUS,
        PushReceipt.ERROR_STATUS,
    ],
)
@pytest.mark.django_db
def test_stores_push_receipt_check_date(
    mock_check_receipts_multiple, ticket1, now, status
):
    mock_check_receipts_multiple.return_value = [
        PushReceipt(
            id=ticket1.external_id,
            status=status,
            message="",
            details=None,
        ),
    ]

    check_receipts([ticket1.pk])

    receipt1 = ticket1.receipts.get()
    assert receipt1.date_checked == now


@pytest.mark.django_db
def test_can_handle_external_ids_omitted_from_response_due_to_being_unknown_to_expo(
    mock_check_receipts_multiple, ticket1, ticket2
):
    assert ticket1.receipts.count() == 0
    assert ticket2.receipts.count() == 0

    mock_check_receipts_multiple.return_value = [
        PushReceipt(
            id=ticket2.external_id,
            status=PushReceipt.SUCCESS_STATUS,
            message="",
            details=None,
        ),
    ]

    check_receipts([ticket1.pk, ticket2.pk])
    assert ticket1.receipts.count() == 0

    receipt2 = ticket2.receipts.get()
    assert receipt2.is_success


@pytest.mark.django_db
def test_tickets_can_be_checked_multiple_times(mock_check_receipts_multiple, ticket1):
    assert ticket1.receipts.count() == 0

    mock_check_receipts_multiple.side_effect = [
        [
            PushReceipt(
                id=ticket1.external_id,
                status=PushReceipt.SUCCESS_STATUS,
                message="",
                details=None,
            ),
        ],
        [
            PushReceipt(
                id=ticket1.external_id,
                status=PushReceipt.SUCCESS_STATUS,
                message="",
                details=None,
            ),
        ],
    ]

    check_receipts([ticket1.pk])
    assert ticket1.receipts.count() == 1

    check_receipts([ticket1.pk])
    assert ticket1.receipts.count() == 2

    receipt1 = ticket1.receipts.all()[0]
    assert receipt1.is_success

    receipt2 = ticket1.receipts.all()[1]
    assert receipt2.is_success
