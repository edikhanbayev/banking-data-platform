import argparse
import random
import uuid

from datetime import (
    datetime,
    timedelta,
)

import psycopg

from src.config import SOURCE_DB


MERCHANTS = [
    (
        "Magnum",
        "GROCERY",
    ),
    (
        "Small",
        "GROCERY",
    ),
    (
        "Kaspi Travel",
        "TRAVEL",
    ),
    (
        "Air Astana",
        "AIRLINE",
    ),
    (
        "Technodom",
        "ELECTRONICS",
    ),
    (
        "Glovo",
        "FOOD",
    ),
    (
        "Yandex Go",
        "TRANSPORT",
    ),
]


def get_account_ids():

    with psycopg.connect(
        **SOURCE_DB
    ) as connection:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT account_id
                FROM accounts
                """
            )

            return [
                row[0]
                for row
                in cursor.fetchall()
            ]


def generate_row(
    account_ids
):

    account_id = random.choice(
        account_ids
    )


    merchant_name, (
        merchant_category
    ) = random.choice(
        MERCHANTS
    )


    transaction_type = (
        random.choice(
            [
                "CARD_PAYMENT",
                "TRANSFER",
                "ATM_WITHDRAWAL",
            ]
        )
    )


    amount = round(
        random.uniform(
            500,
            500_000,
        ),
        2,
    )


    currency = random.choice(
        [
            "KZT",
            "USD",
            "EUR",
        ]
    )


    status = random.choices(
        [
            "COMPLETED",
            "DECLINED",
        ],
        weights=[
            95,
            5,
        ],
    )[0]


    days_back = random.randint(
        0,
        365,
    )


    seconds_back = random.randint(
        0,
        86_400,
    )


    timestamp = (
        datetime.now()
        -
        timedelta(
            days=days_back,
            seconds=seconds_back,
        )
    )


    return (
        uuid.uuid4(),
        account_id,
        transaction_type,
        merchant_name,
        merchant_category,
        amount,
        currency,
        timestamp,
        status,
    )


def generate_transactions(
    count: int
):

    account_ids = (
        get_account_ids()
    )


    if not account_ids:

        raise RuntimeError(
            (
                "No accounts found. "
                "Run seed_data first."
            )
        )


    copy_sql = """
    COPY transactions
    (
        transaction_id,
        account_id,
        transaction_type,
        merchant_name,
        merchant_category,
        amount,
        currency,
        transaction_timestamp,
        status
    )
    FROM STDIN
    """


    with psycopg.connect(
        **SOURCE_DB
    ) as connection:

        with connection.cursor() as cursor:

            with cursor.copy(
                copy_sql
            ) as copy:

                for index in range(
                    count
                ):

                    row = generate_row(
                        account_ids
                    )

                    copy.write_row(
                        row
                    )


                    if (
                        index > 0
                        and
                        index % 100_000
                        == 0
                    ):

                        print(
                            (
                                f"Generated "
                                f"{index:,} "
                                f"rows"
                            )
                        )


        connection.commit()


    print(
        (
            f"Finished: "
            f"{count:,} "
            f"transactions"
        )
    )


def main():

    parser = (
        argparse.ArgumentParser()
    )


    parser.add_argument(
        "--count",
        type=int,
        default=100_000,
    )


    args = (
        parser.parse_args()
    )


    generate_transactions(
        args.count
    )


if __name__ == "__main__":
    main()