import psycopg

from src.config import (
    SOURCE_DB,
    DWH_DB,
)


def load_customers():

    with psycopg.connect(**SOURCE_DB) as source_conn:
        with source_conn.cursor() as source_cursor:

            source_cursor.execute("""
                SELECT
                    customer_id,
                    first_name,
                    last_name,
                    email,
                    country,
                    created_at
                FROM customers
            """)

            customers = source_cursor.fetchall()

    with psycopg.connect(**DWH_DB) as dwh_conn:
        with dwh_conn.cursor() as dwh_cursor:

            dwh_cursor.execute(
                "TRUNCATE TABLE raw.customers"
            )

            dwh_cursor.executemany("""
                INSERT INTO raw.customers (
                    customer_id,
                    first_name,
                    last_name,
                    email,
                    country,
                    created_at
                )
                VALUES (%s, %s, %s, %s, %s, %s)
            """, customers)

        dwh_conn.commit()

    print(
        f"Loaded {len(customers)} customers"
    )


def load_accounts():

    with psycopg.connect(**SOURCE_DB) as source_conn:
        with source_conn.cursor() as source_cursor:

            source_cursor.execute("""
                SELECT
                    account_id,
                    customer_id,
                    account_number,
                    account_type,
                    currency,
                    balance,
                    created_at
                FROM accounts
            """)

            accounts = source_cursor.fetchall()

    with psycopg.connect(**DWH_DB) as dwh_conn:
        with dwh_conn.cursor() as dwh_cursor:

            dwh_cursor.execute(
                "TRUNCATE TABLE raw.accounts"
            )

            dwh_cursor.executemany("""
                INSERT INTO raw.accounts (
                    account_id,
                    customer_id,
                    account_number,
                    account_type,
                    currency,
                    balance,
                    created_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, accounts)

        dwh_conn.commit()

    print(
        f"Loaded {len(accounts)} accounts"
    )


if __name__ == "__main__":
    load_customers()
    load_accounts()