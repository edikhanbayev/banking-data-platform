
-- 1. Daily transaction volume

SELECT
    transaction_date,

    COUNT(*) AS transaction_count,

    SUM(amount) AS total_volume,

    AVG(amount) AS average_transaction

FROM analytics.fact_transactions

WHERE status = 'COMPLETED'

GROUP BY
    transaction_date

ORDER BY
    transaction_date;



-- 2. Decline rate

SELECT

    COUNT(*) FILTER (
        WHERE status = 'DECLINED'
    )::DECIMAL

    /

    NULLIF(
        COUNT(*),
        0
    )

    AS decline_rate

FROM analytics.fact_transactions;



-- 3. Spending by merchant category

SELECT
    merchant_category,

    COUNT(*) AS transactions,

    SUM(amount) AS total_amount,

    AVG(amount) AS average_amount

FROM analytics.fact_transactions

WHERE status = 'COMPLETED'

GROUP BY
    merchant_category

ORDER BY
    total_amount DESC;


-- 4. Transactions by country


SELECT
    c.country,

    COUNT(*) AS transaction_count,

    SUM(f.amount) AS total_amount

FROM analytics.fact_transactions f

JOIN analytics.dim_customer c

    ON f.customer_key =
       c.customer_key

WHERE
    f.status = 'COMPLETED'

GROUP BY
    c.country

ORDER BY
    total_amount DESC;


-- 5. Top customers

SELECT
    c.customer_key,

    c.first_name,

    c.last_name,

    c.country,

    COUNT(*) AS transaction_count,

    SUM(f.amount) AS total_spending

FROM analytics.fact_transactions f

JOIN analytics.dim_customer c

    ON f.customer_key =
       c.customer_key

WHERE
    f.status = 'COMPLETED'

GROUP BY
    c.customer_key,
    c.first_name,
    c.last_name,
    c.country

ORDER BY
    total_spending DESC

LIMIT 20;


-- 6. Transaction type analysis

SELECT
    transaction_type,

    COUNT(*) AS transactions,

    SUM(amount) AS total_amount,

    AVG(amount) AS average_amount

FROM analytics.fact_transactions

GROUP BY
    transaction_type

ORDER BY
    total_amount DESC;


-- 7. Monthly transactions

SELECT

    DATE_TRUNC(
        'month',
        transaction_timestamp
    ) AS month,

    COUNT(*) AS transaction_count,

    SUM(amount) AS transaction_volume

FROM analytics.fact_transactions

WHERE status = 'COMPLETED'

GROUP BY 1

ORDER BY 1;
