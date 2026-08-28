BEGIN;

-- Ексклюзивне блокування рядка лічильника поточної фіскальної серії
SELECT current_number 
FROM fiscal_number_counters 
WHERE series = 'INV-2026' 
FOR UPDATE;

-- Обчислення нового номера
UPDATE fiscal_number_counters 
SET current_number = current_number + 1 
WHERE series = 'INV-2026';

-- Вставка документа із гарантовано неперервним номером
INSERT INTO invoices (invoice_number, amount, created_at)
VALUES ('INV-2026-' || (current_number + 1), 1500.00, NOW());

COMMIT;
