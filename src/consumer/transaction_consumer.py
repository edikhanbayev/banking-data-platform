import json
import logging

import psycopg

from confluent_kafka import (
    Consumer,
    Producer,
)

from src.config import SOURCE_DB


logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s "
        "%(levelname)s "
        "%(name)s "
        "%(message)s"
    ),
)


logger = logging.getLogger(
    __name__
)


consumer = Consumer(
    {
        "bootstrap.servers":
            "localhost:9092",

        "group.id":
            "transaction-db-writer",

        "auto.offset.reset":
            "earliest",

        "enable.auto.commit":
            False,
    }
)


dlq_producer = Producer(
    {
        "bootstrap.servers":
            "localhost:9092"
    }
)


INSERT_SQL = """
INSERT INTO transactions
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
VALUES
(
    %(transaction_id)s,
    %(account_id)s,
    %(transaction_type)s,
    %(merchant_name)s,
    %(merchant_category)s,
    %(amount)s,
    %(currency)s,
    %(transaction_timestamp)s,
    %(status)s
)

ON CONFLICT (transaction_id)
DO NOTHING;
"""


REQUIRED_FIELDS = {
    "transaction_id",
    "account_id",
    "transaction_type",
    "amount",
    "currency",
    "transaction_timestamp",
    "status",
}


def validate_event(
    transaction: dict
):

    missing_fields = (
        REQUIRED_FIELDS
        -
        transaction.keys()
    )


    if missing_fields:

        raise ValueError(
            "Missing fields: "
            + ", ".join(
                sorted(
                    missing_fields
                )
            )
        )


    if transaction["amount"] <= 0:

        raise ValueError(
            "Amount must be positive"
        )


    if transaction[
        "currency"
    ] not in {
        "KZT",
        "USD",
        "EUR",
    }:

        raise ValueError(
            "Unsupported currency"
        )


    if transaction[
        "status"
    ] not in {
        "COMPLETED",
        "DECLINED",
    }:

        raise ValueError(
            "Unsupported status"
        )


def send_to_dlq(
    original_value: bytes,
    error_message: str,
):

    dlq_producer.produce(
        topic=
            "bank.transactions.dlq",

        value=
            original_value,

        headers=[
            (
                "error",
                error_message,
            )
        ],
    )


    dlq_producer.flush(
        timeout=5
    )


def main():

    consumer.subscribe(
        [
            "bank.transactions"
        ]
    )


    logger.info(
        "Consumer started"
    )


    try:

        with psycopg.connect(
            **SOURCE_DB
        ) as connection:

            while True:

                message = (
                    consumer.poll(
                        timeout=1.0
                    )
                )


                if message is None:

                    continue


                if message.error():

                    logger.error(
                        "Kafka error: %s",
                        message.error(),
                    )

                    continue


                raw_value = (
                    message.value()
                )


                try:

                    transaction = (
                        json.loads(
                            raw_value.decode(
                                "utf-8"
                            )
                        )
                    )


                    validate_event(
                        transaction
                    )


                    with (
                        connection.cursor()
                        as cursor
                    ):

                        cursor.execute(
                            INSERT_SQL,
                            transaction,
                        )


                    connection.commit()


                    consumer.commit(
                        message=message,
                        asynchronous=False,
                    )


                    logger.info(
                        "Saved transaction %s",
                        transaction[
                            "transaction_id"
                        ],
                    )


                except Exception as exc:

                    connection.rollback()


                    logger.exception(
                        (
                            "Invalid Kafka "
                            "message. "
                            "Sending to DLQ."
                        )
                    )


                    send_to_dlq(
                        original_value=
                            raw_value,

                        error_message=
                            str(exc),
                    )


                    consumer.commit(
                        message=message,
                        asynchronous=False,
                    )


    finally:

        consumer.close()


if __name__ == "__main__":
    main()