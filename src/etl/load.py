import logging

import psycopg

from psycopg.types.json import Jsonb

from src.config import DWH_DB

from src.etl.audit import (
    start_run,
    finish_run,
    fail_run,
)

from src.etl.extract import (
    extract_transactions,
)

from src.etl.validate import (
    validate_transaction_with_reason,
)


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


INSERT_RAW_SQL = """
INSERT INTO raw.transactions
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
    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s,
    %s
)

ON CONFLICT (transaction_id)
DO NOTHING;
"""


INSERT_REJECTED_SQL = """
INSERT INTO raw.rejected_transactions
(
    transaction_id,
    raw_payload,
    rejection_reason
)
VALUES
(
    %s,
    %s,
    %s
);
"""


def row_to_payload(
    row
):

    return {
        "transaction_id": str(
            row[0]
        ),
        "account_id": row[1],
        "transaction_type": row[2],
        "merchant_name": row[3],
        "merchant_category": row[4],
        "amount": str(
            row[5]
        ),
        "currency": row[6],
        "transaction_timestamp": str(
            row[7]
        ),
        "status": row[8],
    }


def run():

    run_id = start_run(
        "transactions_etl"
    )

    logger.info(
        "Pipeline started. run_id=%s",
        run_id,
    )

    try:

        transactions = (
            extract_transactions()
        )

        rows_extracted = len(
            transactions
        )

        logger.info(
            "Extracted %s rows",
            rows_extracted,
        )


        if not transactions:

            finish_run(
                run_id=run_id,
                rows_extracted=0,
                rows_loaded=0,
                rows_rejected=0,
            )

            logger.info(
                "No new transactions."
            )

            return


        valid_rows = []

        rejected_rows = []


        for transaction in transactions:

            (
                is_valid,
                rejection_reason,
            ) = (
                validate_transaction_with_reason(
                    transaction
                )
            )


            if is_valid:

                valid_rows.append(
                    transaction
                )

            else:

                rejected_rows.append(
                    (
                        transaction,
                        rejection_reason,
                    )
                )


        logger.info(
            "Valid rows: %s",
            len(valid_rows),
        )

        logger.info(
            "Rejected rows: %s",
            len(rejected_rows),
        )


        with psycopg.connect(
            **DWH_DB
        ) as connection:

            with connection.cursor() as cursor:

                rows_loaded = 0


                for row in valid_rows:

                    cursor.execute(
                        INSERT_RAW_SQL,
                        row,
                    )

                    rows_loaded += (
                        cursor.rowcount
                    )


                for (
                    row,
                    rejection_reason,
                ) in rejected_rows:

                    payload = (
                        row_to_payload(
                            row
                        )
                    )

                    cursor.execute(
                        INSERT_REJECTED_SQL,
                        (
                            str(row[0]),
                            Jsonb(payload),
                            rejection_reason,
                        ),
                    )


                latest_timestamp = max(
                    row[7]
                    for row
                    in transactions
                )


                cursor.execute(
                    """
                    UPDATE etl.pipeline_state

                    SET
                        last_processed_timestamp
                            = %s

                    WHERE pipeline_name
                        = 'transactions'
                    """,
                    (
                        latest_timestamp,
                    ),
                )


            connection.commit()


        finish_run(
            run_id=run_id,

            rows_extracted=
                rows_extracted,

            rows_loaded=
                rows_loaded,

            rows_rejected=
                len(rejected_rows),
        )


        logger.info(
            (
                "Pipeline completed. "
                "Extracted=%s "
                "Loaded=%s "
                "Rejected=%s"
            ),
            rows_extracted,
            rows_loaded,
            len(rejected_rows),
        )


    except Exception as exc:

        logger.exception(
            "Transactions ETL failed"
        )

        fail_run(
            run_id=run_id,
            error_message=str(exc),
        )

        raise


if __name__ == "__main__":
    run()