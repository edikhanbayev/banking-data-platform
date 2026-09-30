select
    customer_id,
    first_name,
    last_name,
    email,
    country,
    created_at

from {{ source(
    'banking_raw',
    'customers'
) }}