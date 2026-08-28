-- АТОМАРНА БІЗНЕС-ОПЕРАЦІЯ ТА ФІКСАЦІЯ ПОДІЇ
BEGIN;

-- 1. Мутація бізнес-стану
INSERT INTO orders (id, user_id, amount, status)
VALUES ('ord-98421', 8412, 120000.00, 'PAID');

-- 2. Запис події у вихідну скриньку (в тій самій транзакції)
INSERT INTO outbox (id, aggregate_type, aggregate_id, type, payload)
VALUES (
    'f47ac10b-58cc-4372-a567-0e02b2c3d479',
    'orders',
    'ord-98421',
    'OrderPaid',
    '{"orderId":"ord-98421","amount":120000.00,"currency":"UAH"}'::jsonb
);

-- 3. Атомарна фіксація на диску
COMMIT;
