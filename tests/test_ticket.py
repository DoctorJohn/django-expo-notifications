import pytest

from tests.factories import TicketFactory


@pytest.mark.django_db
def test_str():
    ticket = TicketFactory()
    assert str(ticket) == f"Ticket #{ticket.pk}"
