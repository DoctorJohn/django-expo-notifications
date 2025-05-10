import pytest

from expo_notifications.models import Ticket

from .factories import TicketFactory


@pytest.mark.django_db
def test_queryset_check_receipts_schedules_a_check_receipts_task(
    mock_check_receipts_delay_on_commit,
):
    assert Ticket.objects.count() == 0

    ticket1 = TicketFactory()
    ticket2 = TicketFactory()

    Ticket.objects.all().check_receipts()

    assert mock_check_receipts_delay_on_commit.call_count == 1
    assert mock_check_receipts_delay_on_commit.call_args.args == (
        [ticket1.pk, ticket2.pk],
    )
