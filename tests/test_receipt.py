import pytest

from tests.factories import ReceiptFactory


@pytest.mark.django_db
def test_str():
    receipt = ReceiptFactory()
    assert str(receipt) == f"Receipt #{receipt.pk}"
