-- Канонічний банківський переказ у SQL з перевіркою залишку
BEGIN TRANSACTION;

-- 1. Блокування рядка джерела від паралельних змін (SELECT FOR UPDATE)
SELECT balance FROM accounts WHERE id = 1 FOR UPDATE;

-- 2. Списання коштів із перевіркою обмеження цілісності (CHECK balance >= 0)
UPDATE accounts SET balance = balance - 100 WHERE id = 1;

-- 3. Зарахування коштів одержувачу
UPDATE accounts SET balance = balance + 100 WHERE id = 2;

-- 4. Фіксація змін
COMMIT;
