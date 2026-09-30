from datetime import timedelta

import pendulum

from airflow.sdk import dag

from airflow.providers.standard.operators.bash import (
    BashOperator,
)


@dag(
    dag_id="banking_daily_pipeline",

    schedule="0 1 * * *",

    start_date=pendulum.datetime(
        2026,
        1,
        1,
        tz="UTC"
    ),

    catchup=False,

    default_args={
        "retries": 3,
        "retry_delay": timedelta(
            minutes=2
        ),
    },

    tags=[
        "banking",
        "data-engineering",
    ],
)
def banking_daily_pipeline():

    load_raw_transactions = BashOperator(

        task_id="load_raw_transactions",

        bash_command=(
            "cd /opt/project && "
            "python -m src.etl.load"
        ),
    )


    load_dimensions = BashOperator(

        task_id="load_dimensions",

        bash_command=(
            "cd /opt/project && "
            "python -m src.etl.load_dimensions"
        ),
    )


    dbt_build = BashOperator(

        task_id="dbt_build",

        bash_command=(
            "cd /opt/project/dbt/banking_dwh && "
            "dbt build"
        ),
    )
    data_quality = BashOperator(

        task_id="data_quality",

        bash_command=(
            "cd /opt/project && "
            "python -m src.quality.checks"
        ),
    )
    load_clickhouse = BashOperator(

        task_id="load_clickhouse",

        bash_command=(
            "cd /opt/project && "
            "python -m "
            "src.etl.load_clickhouse"
        ),
    )
    (
        [
            load_raw_transactions,
            load_dimensions,
        ]
        >> dbt_build >> data_quality >> load_clickhouse
    )


banking_daily_pipeline()