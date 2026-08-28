BEGIN TRANSACTION;

-- 1. Спроба вставити ідентифікатор повідомлення
INSERT INTO inbox_messages (message_id, event_type, status, processed_at)
VALUES ('evt-84920', 'OrderPaid', 'PROCESSED', NOW())
ON CONFLICT (message_id) DO NOTHING;

-- Якщо рядок не вставився (rows_affected == 0), це дублікат:
-- негайно робимо COMMIT або ROLLBACK і шлемо ACK брокеру.

-- 2. Виконання бізнес-мутації
UPDATE accounts SET balance = balance - 500 WHERE user_id = 42;
INSERT INTO ledger (order_id, amount) VALUES ('ord-99', 500);

COMMIT;
