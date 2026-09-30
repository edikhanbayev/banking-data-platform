from datetime import datetime

from decimal import Decimal

from uuid import uuid4

from src.etl.validate import (
    validate_transaction,
    validate_transaction_with_reason,
)


def create_valid_row():

    return (
        uuid4(),
        1,
        "CARD_PAYMENT",
        "Magnum",
        "GROCERY",
        Decimal("1000.00"),
        "KZT",
        datetime.now(),
        "COMPLETED",
    )


def test_valid_transaction():

    row = create_valid_row()

    assert (
        validate_transaction(
            row
        )
        is True
    )


def test_negative_amount():

    row = list(
        create_valid_row()
    )

    row[5] = Decimal(
        "-100.00"
    )


    valid, reason = (
        validate_transaction_with_reason(
            tuple(row)
        )
    )


    assert valid is False

    assert (
        "positive"
        in reason
    )


def test_missing_account():

    row = list(
        create_valid_row()
    )

    row[1] = None


    valid, reason = (
        validate_transaction_with_reason(
            tuple(row)
        )
    )


    assert valid is False

    assert (
        reason
        == "account_id is NULL"
    )


def test_invalid_currency():

    row = list(
        create_valid_row()
    )

    row[6] = "GBP"


    valid, reason = (
        validate_transaction_with_reason(
            tuple(row)
        )
    )


    assert valid is False

    assert (
        "unsupported currency"
        in reason
    )


def test_invalid_status():

    row = list(
        create_valid_row()
    )

    row[8] = "UNKNOWN"


    valid, reason = (
        validate_transaction_with_reason(
            tuple(row)
        )
    )


    assert valid is False

    assert (
        "unsupported status"
        in reason
    )