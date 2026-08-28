BEGIN;
INSERT INTO orders (id, customer_id, total, status) VALUES (101, 42, 1500, 'PAID');
INSERT INTO outbox_events (id, aggregate_type, aggregate_id, event_type, payload)
VALUES (
    gen_random_uuid(), 
    'Order', 
    '101', 
    'OrderPaid', 
    '{"order_id": 101, "customer_id": 42, "amount": 1500, "items": [501, 502]}'
);
COMMIT;
