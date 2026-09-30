select
    account_id as account_key,
    customer_id as customer_key,
    account_number,
    account_type,
    currency,
    balance,
    created_at

from {{ ref(
    'stg_accounts'
) }}