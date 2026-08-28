BEGIN;
DECLARE cur_acc CURSOR FOR 
    SELECT balance FROM accounts WHERE status = 'ACTIVE' FOR UPDATE;

FETCH NEXT FROM cur_acc;

-- Миттєве оновлення без повторного пошуку за індексом
UPDATE accounts 
SET balance = balance * 1.05 
WHERE CURRENT OF cur_acc;

CLOSE cur_acc;
COMMIT;
