ALLOWED_CURRENCIES = {
    "KZT",
    "USD",
    "EUR",
}


ALLOWED_STATUSES = {
    "COMPLETED",
    "DECLINED",
}


ALLOWED_TRANSACTION_TYPES = {
    "CARD_PAYMENT",
    "TRANSFER",
    "ATM_WITHDRAWAL",
}


def validate_transaction_with_reason(
    row
):

    (
        transaction_id,
        account_id,
        transaction_type,
        merchant_name,
        merchant_category,
        amount,
        currency,
        transaction_timestamp,
        status,
    ) = row

    if transaction_id is None:
        return False, "transaction_id is NULL"

    if account_id is None:
        return False, "account_id is NULL"

    if transaction_type not in (
        ALLOWED_TRANSACTION_TYPES
    ):
        return (
            False,
            (
                "unsupported "
                f"transaction_type: "
                f"{transaction_type}"
            ),
        )

    if amount is None:
        return False, "amount is NULL"

    if amount <= 0:
        return (
            False,
            f"amount must be positive: {amount}",
        )

    if currency not in ALLOWED_CURRENCIES:
        return (
            False,
            f"unsupported currency: {currency}",
        )

    if transaction_timestamp is None:
        return (
            False,
            "transaction_timestamp is NULL",
        )

    if status not in ALLOWED_STATUSES:
        return (
            False,
            f"unsupported status: {status}",
        )

    return True, None


def validate_transaction(
    row
):

    valid, _ = (
        validate_transaction_with_reason(
            row
        )
    )

    return valid