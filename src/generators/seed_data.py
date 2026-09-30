import random

import psycopg
from faker import Faker


fake = Faker()


DB_CONFIG = {
    "host": "localhost",
    "port": 15432,
    "dbname": "banking",
    "user": "banking",
    "password": "banking",
}


def create_customers(cursor, count=1000):

    customer_ids = []

    for _ in range(count):

        first_name = fake.first_name()
        last_name = fake.last_name()

        email = fake.unique.email()

        country = random.choice([
            "Kazakhstan",
            "Kyrgyzstan",
            "Uzbekistan"
        ])

        cursor.execute(
            """
            INSERT INTO customers (
                first_name,
                last_name,
                email,
                country
            )
            VALUES (%s, %s, %s, %s)
            RETURNING customer_id
            """,
            (
                first_name,
                last_name,
                email,
                country
            )
        )

        customer_id = cursor.fetchone()[0]

        customer_ids.append(customer_id)

    return customer_ids


def create_accounts(cursor, customer_ids):

    for customer_id in customer_ids:

        account_number = fake.iban()

        account_type = random.choice([
            "CHECKING",
            "SAVINGS"
        ])

        currency = random.choice([
            "KZT",
            "USD",
            "EUR"
        ])

        balance = random.uniform(
            10_000,
            5_000_000
        )

        cursor.execute(
            """
            INSERT INTO accounts (
                customer_id,
                account_number,
                account_type,
                currency,
                balance
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                customer_id,
                account_number,
                account_type,
                currency,
                balance
            )
        )


def main():

    with psycopg.connect(**DB_CONFIG) as connection:

        with connection.cursor() as cursor:

            customer_ids = create_customers(
                cursor,
                count=1000
            )

            create_accounts(
                cursor,
                customer_ids
            )

        connection.commit()

    print("Seed data created successfully.")


if __name__ == "__main__":
    main()