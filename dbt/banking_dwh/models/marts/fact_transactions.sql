select
    t.transaction_id,

    t.account_id as account_key,

    a.customer_id as customer_key,

    t.merchant_name,

    t.merchant_category,

    t.transaction_type,

    t.amount,

    t.currency,

    t.status,

    t.transaction_timestamp,

    cast(
        t.transaction_timestamp as date
    ) as transaction_date

from {{ ref(
    'stg_transactions'
) }} t

left join {{ ref(
    'stg_accounts'
) }} a

    on t.account_id =
       a.account_id