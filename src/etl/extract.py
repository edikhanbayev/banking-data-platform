import psycopg
from src.config import (
    SOURCE_DB,
    DWH_DB,
)


def get_watermark():

    with psycopg.connect(
        **DWH_DB
    ) as connection:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    last_processed_timestamp
                FROM etl.pipeline_state
                WHERE pipeline_name =
                      'transactions'
                """
            )

            return cursor.fetchone()[0]


def extract_transactions():

    watermark = get_watermark()

    with psycopg.connect(
        **SOURCE_DB
    ) as connection:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    transaction_id,
                    account_id,
                    transaction_type,
                    merchant_name,
                    merchant_category,
                    amount,
                    currency,
                    transaction_timestamp,
                    status
                FROM transactions
                WHERE transaction_timestamp > %s
                ORDER BY transaction_timestamp
                """,
                (watermark,)
            )

            return cursor.fetchall()