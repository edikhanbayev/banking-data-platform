select

    transaction_id,

    account_id,

    transaction_type,

    merchant_name,

    merchant_category,

    amount,

    upper(currency)
        as currency,

    transaction_timestamp,

    status,

    loaded_at

from {{ source(
    'banking_raw',
    'transactions'
) }}