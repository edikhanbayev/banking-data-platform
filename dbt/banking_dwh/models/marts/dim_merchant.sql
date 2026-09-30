select distinct
    merchant_name,
    merchant_category

from {{ ref(
    'stg_transactions'
) }}

where merchant_name is not null