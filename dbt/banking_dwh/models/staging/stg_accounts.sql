select
    account_id,
    customer_id,
    account_number,
    account_type,
    upper(currency) as currency,
    balance,
    created_at

from {{ source(
    'banking_raw',
    'accounts'
) }}