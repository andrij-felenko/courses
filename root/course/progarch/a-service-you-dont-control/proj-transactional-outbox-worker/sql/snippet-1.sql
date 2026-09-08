BEGIN;
-- 1. Мутація стану власного домену (наприклад, створення замовлення)
INSERT INTO orders (id, customer_id, total_amount, status)
VALUES ('ORD-101', 'CUST-42', 450.00, 'PENDING_PAYMENT');

-- 2. Атомарне збереження наміру виклику зовнішнього платіжного шлюзу
INSERT INTO outbox_events (
    id, aggregate_type, aggregate_id, event_type, payload,
    idempotency_key, status, next_retry_at
) VALUES (
    'e5b9f71c-3b91-4c12-9c3f-7e28329b3f11', 'Order', 'ORD-101', 'PaymentRequested',
    '{"orderId": "ORD-101", "amount": 450.0, "currency": "UAH"}'::jsonb,
    'idem-ORD-101-v1', 'PENDING', NOW()
);
COMMIT;
