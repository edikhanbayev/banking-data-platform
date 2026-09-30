import psycopg

from src.config import DWH_DB


def execute_check(
    query: str,
    check_name: str,
):

    with psycopg.connect(
        **DWH_DB
    ) as connection:

        with connection.cursor() as cursor:

            cursor.execute(query)

            result = cursor.fetchone()[0]


    if result != 0:

        raise ValueError(
            f"{check_name} failed. "
            f"Invalid rows: {result}"
        )


    print(
        f"{check_name}: PASSED"
    )

def check_freshness():

    query = """
        SELECT
            EXTRACT(
                EPOCH FROM (
                    CURRENT_TIMESTAMP
                    -
                    MAX(transaction_timestamp)
                )
            ) / 3600
        FROM raw.transactions
    """


    with psycopg.connect(
        **DWH_DB
    ) as connection:

        with connection.cursor() as cursor:

            cursor.execute(query)

            hours_old = cursor.fetchone()[0]


    if hours_old is None:

        raise ValueError(
            "No transactions found."
        )


    if hours_old > 48:

        raise ValueError(
            f"Data too old: "
            f"{hours_old:.2f} hours"
        )


    print(
        f"Freshness PASSED: "
        f"{hours_old:.2f} hours"
    )

def main():

    execute_check(
        """
        SELECT COUNT(*)
        FROM analytics.fact_transactions
        WHERE transaction_id IS NULL
        """,
        "null_transaction_id"
    )


    execute_check(
        """
        SELECT COUNT(*)
        FROM (
            SELECT transaction_id
            FROM analytics.fact_transactions
            GROUP BY transaction_id
            HAVING COUNT(*) > 1
        ) duplicates
        """,
        "duplicate_transactions"
    )


    execute_check(
        """
        SELECT COUNT(*)
        FROM analytics.fact_transactions
        WHERE amount <= 0
        """,
        "invalid_amount"
    )


    execute_check(
        """
        SELECT COUNT(*)
        FROM analytics.fact_transactions
        WHERE customer_key IS NULL
        """,
        "missing_customer"
    )
    check_freshness()

if __name__ == "__main__":
    main()