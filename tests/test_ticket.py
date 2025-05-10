import pytest
from exponent_server_sdk import PushTicket

from .factories import TicketFactory


@pytest.mark.django_db
def test_str():
    ticket = TicketFactory()
    assert str(ticket) == f"Ticket #{ticket.pk}"


@pytest.mark.django_db
def test_to_push_ticket_sets_push_message():
    ticket = TicketFactory()
    push_ticket = ticket.to_push_ticket()
    assert push_ticket.push_message == ticket.message.to_push_message()


@pytest.mark.parametrize(
    ("is_success", "status"),
    [(True, PushTicket.SUCCESS_STATUS), (False, PushTicket.ERROR_STATUS)],
)
@pytest.mark.django_db
def test_to_push_ticket_converts_is_success_to_status(is_success, status):
    ticket = TicketFactory(is_success=is_success)
    push_ticket = ticket.to_push_ticket()
    assert push_ticket.status == status


@pytest.mark.django_db
def test_to_push_ticket_converts_blank_error_message_to_none():
    ticket = TicketFactory(error_message="")
    push_ticket = ticket.to_push_ticket()
    assert push_ticket.message is None


@pytest.mark.django_db
def test_to_push_ticket_passes_error_message_through():
    ticket = TicketFactory(error_message="something went wrong")
    push_ticket = ticket.to_push_ticket()
    assert push_ticket.message == ticket.error_message


@pytest.mark.django_db
def test_to_push_ticket_leaves_details_blank():
    ticket = TicketFactory()
    push_ticket = ticket.to_push_ticket()
    assert push_ticket.details is None


@pytest.mark.django_db
def test_to_push_ticket_sets_external_id_as_id():
    ticket = TicketFactory(external_id="test-external-id")
    push_ticket = ticket.to_push_ticket()
    assert push_ticket.id == "test-external-id"


@pytest.mark.django_db
def test_check_receipt_schedules_a_check_receipts_task(
    mock_check_receipts_delay_on_commit,
):
    ticket = TicketFactory()
    ticket.check_receipt()
    assert mock_check_receipts_delay_on_commit.call_count == 1
    assert mock_check_receipts_delay_on_commit.call_args.args == ([ticket.pk],)
