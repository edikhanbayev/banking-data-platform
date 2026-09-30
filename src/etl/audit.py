from datetime import datetime, timezone

import psycopg

from src.config import DWH_DB


def start_run(
    pipeline_name: str
) -> int:

    started_at = datetime.now(
        timezone.utc
    )

    with psycopg.connect(
        **DWH_DB
    ) as connection:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO etl.pipeline_runs
                (
                    pipeline_name,
                    started_at,
                    status
                )
                VALUES
                (
                    %s,
                    %s,
                    'RUNNING'
                )
                RETURNING run_id
                """,
                (
                    pipeline_name,
                    started_at,
                ),
            )

            run_id = cursor.fetchone()[0]

        connection.commit()

    return run_id


def finish_run(
    run_id: int,
    rows_extracted: int,
    rows_loaded: int,
    rows_rejected: int,
) -> None:

    finished_at = datetime.now(
        timezone.utc
    )

    with psycopg.connect(
        **DWH_DB
    ) as connection:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                UPDATE etl.pipeline_runs

                SET
                    finished_at = %s,
                    rows_extracted = %s,
                    rows_loaded = %s,
                    rows_rejected = %s,
                    status = 'SUCCESS',
                    error_message = NULL

                WHERE run_id = %s
                """,
                (
                    finished_at,
                    rows_extracted,
                    rows_loaded,
                    rows_rejected,
                    run_id,
                ),
            )

        connection.commit()


def fail_run(
    run_id: int,
    error_message: str
) -> None:

    finished_at = datetime.now(
        timezone.utc
    )

    with psycopg.connect(
        **DWH_DB
    ) as connection:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                UPDATE etl.pipeline_runs

                SET
                    finished_at = %s,
                    status = 'FAILED',
                    error_message = %s

                WHERE run_id = %s
                """,
                (
                    finished_at,
                    error_message,
                    run_id,
                ),
            )

        connection.commit()