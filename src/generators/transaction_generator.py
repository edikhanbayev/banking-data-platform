import random
import uuid

from datetime import datetime, timezone


MERCHANTS = [
    ("Magnum", "GROCERY"),
    ("Small", "GROCERY"),
    ("Kaspi Travel", "TRAVEL"),
    ("Air Astana", "AIRLINE"),
    ("Technodom", "ELECTRONICS"),
    ("Glovo", "FOOD"),
    ("Yandex Go", "TRANSPORT"),
]


def generate_transaction(account_id: int):

    merchant_name, merchant_category = random.choice(
        MERCHANTS
    )

    return {

        "transaction_id": str(uuid.uuid4()),

        "account_id": account_id,

        "transaction_type": random.choice([
            "CARD_PAYMENT",
            "TRANSFER",
            "ATM_WITHDRAWAL"
        ]),

        "merchant_name": merchant_name,

        "merchant_category": merchant_category,

        "amount": round(
            random.uniform(
                500,
                500_000
            ),
            2
        ),

        "currency": random.choice([
            "KZT",
            "USD"
        ]),

        "transaction_timestamp":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "status": random.choices(
            [
                "COMPLETED",
                "DECLINED"
            ],
            weights=[
                95,
                5
            ]
        )[0]
    }