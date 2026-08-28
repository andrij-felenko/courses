SELECT 
    o.order_id,
    o.amount,
    o.event_time,
    t.tariff_tier,
    (o.amount * (100 - t.discount_pct) / 100) AS final_amount
FROM raw_orders o
LEFT JOIN dim_user_tariffs t 
    ON o.user_id = t.user_id
   AND o.event_time >= t.valid_from 
   AND o.event_time <  t.valid_to;
