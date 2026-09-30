import os

import clickhouse_connect
import psycopg

from src.config import DWH_DB


CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST", "localhost")

CLICKHOUSE_PORT = int(
    os.getenv(
        "CLICKHOUSE_PORT",
        "8123"
    )
)
CLICKHOUSE_DB = os.getenv("CLICKHOUSE_DB", "banking")
CLICKHOUSE_USER =os.getenv("CLICKHOUSE_USER", "banking")
CLICKHOUSE_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD", "banking")

def extract_from_dwh():

    with psycopg.connect(
        **DWH_DB
    ) as connection:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    transaction_id,
                    account_key,
                    customer_key,
                    merchant_name,
                    merchant_category,
                    transaction_type,
                    amount,
                    currency,
                    status,
                    transaction_timestamp,
                    transaction_date
                FROM analytics.fact_transactions
                """
            )

            return cursor.fetchall()


def load():

    rows = extract_from_dwh()


    if not rows:

        print(
            "No rows to load."
        )

        return


    client = (
        clickhouse_connect
        .get_client(
            host=CLICKHOUSE_HOST,
            port=CLICKHOUSE_PORT,
            username=CLICKHOUSE_USER,
            password=CLICKHOUSE_PASSWORD,
            database=CLICKHOUSE_DB,
        )
    )


    client.command(
        "TRUNCATE TABLE banking.transactions"
    )


    client.insert(
        "banking.transactions",

        rows,

        column_names=[
            "transaction_id",
            "account_key",
            "customer_key",
            "merchant_name",
            "merchant_category",
            "transaction_type",
            "amount",
            "currency",
            "status",
            "transaction_timestamp",
            "transaction_date",
        ],
    )


    print(
        f"Loaded "
        f"{len(rows)} "
        f"rows into ClickHouse."
    )


if __name__ == "__main__":
    load()