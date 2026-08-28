BEGIN TRANSACTION;

-- 1. Спроба вставити ключ ідемпотентності
INSERT INTO idempotency_keys (key, payload_hash, status, response_code, response_body, expires_at)
VALUES ('req-uuid-9948', 'sha256_abc123', 'COMMITTED', 200, '{"tx_id": 8812}', NOW() + INTERVAL '24 hours')
ON CONFLICT (key) DO NOTHING;

-- 2. Перевіряємо, чи вставився рядок (якщо 0 рядків — ключ вже був використаний)
-- Якщо рядок новий — виконуємо бізнес-мутацію в цій же транзакції:
UPDATE accounts SET balance = balance - 1000 WHERE id = 42;

COMMIT;
