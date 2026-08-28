BEGIN;

INSERT INTO orders (id, user_id, amount, status) 
VALUES ('ord_101', 'usr_55', 10000, 'paid');

INSERT INTO outbox_events (
    id, tenant_id, destination_url, secret_key, 
    event_type, payload, status, next_retry_at
) VALUES (
    'evt_999', 'tenant_abc', 'https://shop.example.com/webhooks', 'whsec_xyz',
    'order.paid', '{"order_id": "ord_101", "amount": 10000}', 'pending', NOW()
);

COMMIT;
