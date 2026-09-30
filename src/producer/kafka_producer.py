import json
import random
import time

import psycopg

from confluent_kafka import Producer

from src.generators.transaction_generator import (
    generate_transaction
)

DB_CONFIG = {
    "host": "localhost",
    "port": 15432,
    "dbname": "banking",
    "user": "banking",
    "password": "banking",
}

producer = Producer({
    "bootstrap.servers": "localhost:9092"
})

def get_account_ids():

    with psycopg.connect(
        **DB_CONFIG
    ) as connection:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT account_id
                FROM accounts
                """
            )

            rows = cursor.fetchall()

            return [
                row[0]
                for row in rows
            ]


def delivery_report(
    error,
    message
):

    if error:

        print(
            f"Delivery failed: {error}"
        )

    else:

        print(
            f"Delivered to "
            f"{message.topic()} "
            f"partition "
            f"{message.partition()}"
        )


def main():

    account_ids = get_account_ids()

    while True:

        account_id = random.choice(
            account_ids
        )

        transaction = (
            generate_transaction(
                account_id
            )
        )

        producer.produce(
            topic="bank.transactions",

            key=str(account_id),

            value=json.dumps(
                transaction
            ),

            callback=delivery_report
        )

        producer.poll(0)

        print(transaction)

        time.sleep(0.5)


if __name__ == "__main__":
    main()