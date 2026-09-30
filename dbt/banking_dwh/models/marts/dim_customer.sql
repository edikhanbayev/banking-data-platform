select
    customer_id as customer_key,
    first_name,
    last_name,
    email,
    country,
    created_at

from {{ ref(
    'stg_customers'
) }}