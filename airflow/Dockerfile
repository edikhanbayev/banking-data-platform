FROM apache/airflow:3.3.2-python3.12

USER airflow

RUN pip install --no-cache-dir \
    "psycopg[binary]" \
    dbt-postgres \
    clickhouse-connect