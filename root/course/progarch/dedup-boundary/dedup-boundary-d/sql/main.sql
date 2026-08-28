BEGIN TRANSACTION;

-- 1. Спроба вставити ключ ідемпотентності
INSERT INTO processed_keys (key, response_payload, created_at)
VALUES ('REQ-PAYMENT-99812', '{"status":"ok"}', NOW());

-- 2. Якщо ключ вже існує — виникне UNIQUE Constraint Violation (ERR 23505)
-- Транзакція негайно відкочується, бізнес-логіка повертає збережений payload.

-- 3. Виконання основних бізнес-мутацій
UPDATE accounts SET balance = balance - 1500 WHERE account_id = 'ACC-90412';
INSERT INTO payment_transactions (id, account_id, amount) VALUES ('TX-100', 'ACC-90412', 1500);

COMMIT TRANSACTION;
