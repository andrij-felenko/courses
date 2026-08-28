BEGIN;
-- Встановлюємо локальний прапорець сесії лише на час поточної транзакції
SET LOCAL app.override_soft_delete = 'true';

-- Запит повертає як активні, так і м'яко видалені рядки
SELECT id, email, deleted_at FROM accounts WHERE id = 42;

-- Відновлення запису
UPDATE accounts SET deleted_at = NULL WHERE id = 42;
COMMIT;
