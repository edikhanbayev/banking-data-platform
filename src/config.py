import os


SOURCE_DB = {
    "host": os.getenv(
        "SOURCE_DB_HOST",
        "localhost"
    ),
    "port": int(
        os.getenv(
            "SOURCE_DB_PORT",
            "15432"
        )
    ),
    "dbname": os.getenv(
        "SOURCE_DB_NAME",
        "banking"
    ),
    "user": os.getenv(
        "SOURCE_DB_USER",
        "banking"
    ),
    "password": os.getenv(
        "SOURCE_DB_PASSWORD",
        "banking"
    ),
}


DWH_DB = {
    "host": os.getenv(
        "DWH_DB_HOST",
        "localhost"
    ),
    "port": int(
        os.getenv(
            "DWH_DB_PORT",
            "5433"
        )
    ),
    "dbname": os.getenv(
        "DWH_DB_NAME",
        "banking_dwh"
    ),
    "user": os.getenv(
        "DWH_DB_USER",
        "dwh"
    ),
    "password": os.getenv(
        "DWH_DB_PASSWORD",
        "dwh"
    ),
}