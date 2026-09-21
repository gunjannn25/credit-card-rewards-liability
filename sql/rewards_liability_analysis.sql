CREATE DATABASE IF NOT EXISTS rewards_liability_db;
USE rewards_liability_db;

DROP TABLE IF EXISTS modeled_reward_issuances;
DROP TABLE IF EXISTS card_accounts;

CREATE TABLE modeled_reward_issuances (
    rewards_account_id VARCHAR(30),
    user_id INT,
    card_id INT,
    transaction_date DATE,
    transaction_amount_usd DECIMAL(12,2),
    mcc INT,
    spend_category VARCHAR(20),
    points_per_usd INT,
    points_issued INT,
    age_months INT,
    redemption_development_pct DECIMAL(8,4),
    expected_ultimate_redemption_points DECIMAL(14,2),
    modeled_redeemed_to_date DECIMAL(14,2),
    outstanding_expected_redemption_points DECIMAL(14,2),
    modeled_liability_usd DECIMAL(14,2),
    is_expired BOOLEAN
);

LOAD DATA LOCAL INFILE
'C:/Users/lenovo/Desktop/credit_card_liability/data_modeled/modeled_rewards_liability.csv'
INTO TABLE modeled_reward_issuances
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

CREATE TABLE card_accounts AS
SELECT
    rewards_account_id,
    user_id,
    card_id,
    MIN(transaction_date) AS first_transaction_date,
    MAX(transaction_date) AS last_transaction_date,
    COUNT(*) AS transaction_count,
    SUM(transaction_amount_usd) AS total_spend_usd,
    SUM(points_issued) AS total_points_issued,
    SUM(modeled_liability_usd) AS outstanding_liability_usd
FROM modeled_reward_issuances
GROUP BY rewards_account_id, user_id, card_id;

SELECT COUNT(*) AS loaded_transaction_rows
FROM modeled_reward_issuances;

SELECT *
FROM card_accounts;

USE rewards_liability_db;

-- Executive KPI summary
SELECT
    COUNT(*) AS transaction_count,
    ROUND(SUM(transaction_amount_usd), 2) AS total_source_spend_usd,
    SUM(points_issued) AS modeled_points_issued,
    ROUND(SUM(modeled_redeemed_to_date), 2) AS modeled_points_redeemed_to_date,
    ROUND(SUM(modeled_liability_usd), 2) AS modeled_outstanding_liability_usd,
    ROUND(
        100 * SUM(modeled_liability_usd) / NULLIF(SUM(points_issued) * 0.01, 0),
        2
    ) AS outstanding_liability_pct_of_gross_point_cost
FROM modeled_reward_issuances;

-- Liability concentration by spend category
WITH category_liability AS (
    SELECT
        spend_category,
        ROUND(SUM(transaction_amount_usd), 2) AS source_spend_usd,
        SUM(points_issued) AS modeled_points_issued,
        ROUND(SUM(modeled_liability_usd), 2) AS modeled_liability_usd
    FROM modeled_reward_issuances
    GROUP BY spend_category
)
SELECT
    spend_category,
    source_spend_usd,
    modeled_points_issued,
    modeled_liability_usd,
    ROUND(
        100 * modeled_liability_usd
        / SUM(modeled_liability_usd) OVER (),
        2
    ) AS liability_share_pct,
    ROUND(
        100 * SUM(modeled_liability_usd) OVER (
            ORDER BY modeled_liability_usd DESC
        )
        / SUM(modeled_liability_usd) OVER (),
        2
    ) AS cumulative_liability_share_pct
FROM category_liability
ORDER BY modeled_liability_usd DESC;

USE rewards_liability_db;

SELECT
    COUNT(*) AS row_count,
    COUNT(DISTINCT rewards_account_id) AS accounts,
    COUNT(DISTINCT user_id) AS users,
    COUNT(DISTINCT card_id) AS cards,
    MIN(transaction_date) AS first_transaction,
    MAX(transaction_date) AS last_transaction,
    ROUND(SUM(transaction_amount_usd),2) AS total_spend_usd,
    SUM(points_issued) AS total_points_issued,
    ROUND(SUM(modeled_redeemed_to_date),2) AS total_redeemed_points,
    ROUND(SUM(outstanding_redemption_points),2) AS total_outstanding_points,
    ROUND(SUM(modeled_liability_usd),2) AS total_liability_usd
FROM modeled_reward_issuances;

USE rewards_liability_db;

DESCRIBE modeled_reward_issuances;

USE rewards_liability_db;

SELECT
    COUNT(*) AS transaction_rows,
    COUNT(DISTINCT card_id) AS cards,
    MIN(transaction_date) AS first_transaction,
    MAX(transaction_date) AS last_transaction,
    ROUND(SUM(transaction_amount_usd), 2) AS total_spend_usd,
    SUM(points_issued) AS total_points_issued,
    ROUND(SUM(modeled_redeemed_to_date), 2) AS redeemed_points,
    ROUND(SUM(outstanding_expected_redemption_points), 2) AS outstanding_points,
    ROUND(SUM(modeled_liability_usd), 2) AS estimated_liability_usd
FROM modeled_reward_issuances;

SELECT
    card_id,
    COUNT(*) AS transaction_count,
    ROUND(SUM(transaction_amount_usd), 2) AS total_spend_usd,
    SUM(points_issued) AS points_issued,
    ROUND(SUM(modeled_redeemed_to_date), 2) AS redeemed_points,
    ROUND(SUM(outstanding_expected_redemption_points), 2) AS outstanding_points,
    ROUND(SUM(modeled_liability_usd), 2) AS liability_usd,
    ROUND(
        100 * SUM(modeled_liability_usd)
        / NULLIF(SUM(SUM(modeled_liability_usd)) OVER (), 0),
        2
    ) AS liability_share_pct
FROM modeled_reward_issuances
GROUP BY card_id
ORDER BY liability_usd DESC;


USE rewards_liability_db;

WITH monthly AS (
    SELECT
        DATE_FORMAT(transaction_date, '%Y-%m') AS transaction_month,
        ROUND(SUM(transaction_amount_usd), 2) AS spend_usd,
        SUM(points_issued) AS points_issued,
        ROUND(SUM(modeled_redeemed_to_date), 2) AS redeemed_points,
        ROUND(SUM(outstanding_expected_redemption_points), 2) AS outstanding_points,
        ROUND(SUM(modeled_liability_usd), 2) AS liability_usd
    FROM modeled_reward_issuances
    GROUP BY DATE_FORMAT(transaction_date, '%Y-%m')
)

SELECT
    transaction_month,
    spend_usd,
    points_issued,
    redeemed_points,
    outstanding_points,
    liability_usd,

    LAG(liability_usd) OVER (
        ORDER BY transaction_month
    ) AS prior_month_liability,

    ROUND(
        liability_usd -
        LAG(liability_usd) OVER (
            ORDER BY transaction_month
        ),
        2
    ) AS liability_variance_usd,

    ROUND(
        100 * (
            liability_usd /
            NULLIF(
                LAG(liability_usd) OVER (
                    ORDER BY transaction_month
                ), 0
            ) - 1
        ),
        2
    ) AS liability_variance_pct

FROM monthly
ORDER BY transaction_month;


USE rewards_liability_db;

WITH monthly AS (
    SELECT
        DATE_FORMAT(transaction_date, '%Y-%m') AS transaction_month,
        ROUND(SUM(transaction_amount_usd), 2) AS spend_usd,
        SUM(points_issued) AS points_issued,
        ROUND(SUM(modeled_redeemed_to_date), 2) AS redeemed_points,
        ROUND(SUM(outstanding_expected_redemption_points), 2) AS outstanding_points,
        ROUND(SUM(modeled_liability_usd), 2) AS liability_usd
    FROM modeled_reward_issuances
    GROUP BY DATE_FORMAT(transaction_date, '%Y-%m')
)

SELECT
    transaction_month,
    spend_usd,
    points_issued,
    redeemed_points,
    outstanding_points,
    liability_usd,

    LAG(liability_usd) OVER (
        ORDER BY transaction_month
    ) AS prior_month_liability,

    ROUND(
        liability_usd -
        LAG(liability_usd) OVER (
            ORDER BY transaction_month
        ), 2
    ) AS liability_variance_usd,

    ROUND(
        100 * (
            liability_usd /
            NULLIF(
                LAG(liability_usd) OVER (
                    ORDER BY transaction_month
                ), 0
            ) - 1
        ), 2
    ) AS liability_variance_pct

FROM monthly
ORDER BY transaction_month;


USE rewards_liability_db;

SELECT
    age_months AS development_month,

    COUNT(*) AS transaction_count,

    SUM(points_issued) AS points_issued,

    ROUND(
        SUM(modeled_redeemed_to_date), 2
    ) AS redeemed_points,

    ROUND(
        SUM(outstanding_expected_redemption_points), 2
    ) AS outstanding_points,

    ROUND(
        100 * SUM(modeled_redeemed_to_date)
        / NULLIF(SUM(points_issued), 0),
        2
    ) AS observed_modeled_redemption_pct,

    ROUND(
        SUM(modeled_liability_usd), 2
    ) AS liability_usd

FROM modeled_reward_issuances

GROUP BY age_months

ORDER BY age_months;





USE rewards_liability_db;

WITH base AS (
    SELECT
        points_issued,
        age_months
    FROM modeled_reward_issuances
),

scenarios AS (
    SELECT 0.88 AS urr
    UNION ALL SELECT 0.90
    UNION ALL SELECT 0.92
    UNION ALL SELECT 0.94
    UNION ALL SELECT 0.96
),

scenario_liability AS (
    SELECT
        s.urr,
        SUM(
            points_issued *
            (
                1 -
                LEAST(
                    s.urr,
                    s.urr * (age_months / 24.0)
                )
            )
        ) * 0.01 AS estimated_liability_usd
    FROM base
    CROSS JOIN scenarios s
    GROUP BY s.urr
)

SELECT
    ROUND(urr * 100, 2) AS ultimate_redemption_rate_pct,
    ROUND(estimated_liability_usd, 2) AS estimated_liability_usd,
    ROUND(
        estimated_liability_usd -
        MAX(CASE WHEN urr = 0.92
                 THEN estimated_liability_usd END) OVER (),
        2
    ) AS change_vs_92pct_baseline
FROM scenario_liability
ORDER BY urr;