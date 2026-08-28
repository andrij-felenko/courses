BEGIN;

-- 1. Спроба зареєструвати унікальний ідентифікатор вхідної події
INSERT INTO inbox (message_id, handler_name, received_at)
VALUES ('f47ac10b-58cc-4372-a567-0e02b2c3d479', 'PaymentProcessor', NOW())
ON CONFLICT (message_id) DO NOTHING;

-- 2. Якщо вставка повернула 0 змінених рядків (дублікат) — скасовуємо бізнес-дію
-- Якщо вставка успішна (1 рядок) — виконуємо мутацію бізнес-стану:
UPDATE inventory SET stock = stock - 1 WHERE sku = 'SRV-XEON-64G';

COMMIT;
