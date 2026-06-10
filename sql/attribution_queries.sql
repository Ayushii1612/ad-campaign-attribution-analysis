-- Q1: Customer journey reconstruction
SELECT
    customer_id,
    channel,
    touchpoint_timestamp,
    converted,
    ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY touchpoint_timestamp ASC) AS touchpoint_position,
    COUNT(*) OVER (PARTITION BY customer_id) AS journey_length,
    FIRST_VALUE(channel) OVER (PARTITION BY customer_id ORDER BY touchpoint_timestamp ASC) AS first_channel,
    LAST_VALUE(channel) OVER (PARTITION BY customer_id ORDER BY touchpoint_timestamp ASC
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_channel
FROM customer_journeys
WHERE converted = 1
ORDER BY customer_id, touchpoint_position;

-- Q2: Channel aggregation — clicks vs conversions
SELECT
    channel,
    COUNT(*) AS total_touchpoints,
    SUM(CASE WHEN converted = 1 THEN 1 ELSE 0 END) AS conversions,
    ROUND(1.0 * SUM(CASE WHEN converted = 1 THEN 1 ELSE 0 END) / COUNT(*), 4) AS conversion_rate,
    ROUND(SUM(ad_spend), 2) AS total_ad_spend,
    ROUND(SUM(revenue), 2) AS total_revenue,
    ROUND(SUM(revenue) / NULLIF(SUM(ad_spend), 0), 3) AS roas
FROM customer_journeys
GROUP BY channel
ORDER BY roas DESC;

-- Q3: Last-click attribution in SQL
WITH ranked AS (
    SELECT customer_id, channel, revenue,
        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY touchpoint_timestamp DESC) AS rn
    FROM customer_journeys WHERE converted = 1
)
SELECT
    channel,
    COUNT(*) AS conversions,
    SUM(revenue) AS attributed_revenue,
    ROUND(100.0 * SUM(revenue) / SUM(SUM(revenue)) OVER (), 2) AS revenue_share_pct
FROM ranked WHERE rn = 1
GROUP BY channel
ORDER BY attributed_revenue DESC;

-- Q4: Cohort analysis — conversion by week
SELECT
    strftime('%Y-W%W', touchpoint_timestamp) AS week,
    channel,
    COUNT(DISTINCT customer_id) AS unique_customers,
    SUM(CASE WHEN converted = 1 THEN 1 ELSE 0 END) AS conversions,
    ROUND(SUM(revenue), 2) AS weekly_revenue
FROM customer_journeys
GROUP BY week, channel
ORDER BY week, channel;

-- Q5: Fraud — click velocity per campaign per hour
SELECT
    campaign_id, channel,
    strftime('%Y-%m-%d %H:00', touchpoint_timestamp) AS hour_bucket,
    COUNT(*) AS clicks_in_hour,
    ROUND(COUNT(*) / 3600.0, 2) AS clicks_per_second
FROM customer_journeys
GROUP BY campaign_id, channel, hour_bucket
HAVING clicks_per_second > 1.0
ORDER BY clicks_per_second DESC;

-- Q6: Impossible conversion paths
SELECT
    customer_id, channel, campaign_id,
    touchpoint_timestamp, conversion_timestamp,
    ROUND((julianday(touchpoint_timestamp) - julianday(conversion_timestamp)) * 24, 2)
        AS hours_touch_after_conversion
FROM customer_journeys
WHERE converted = 1 AND conversion_timestamp < touchpoint_timestamp
ORDER BY hours_touch_after_conversion DESC;