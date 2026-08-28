-- 1. Відкриття транзакції та виконання операцій
BEGIN;
UPDATE accounts SET balance = balance - 500 WHERE id = 101;

-- 2. Фаза 1: підготовка та скидання стану на диск (аналог xa_prepare)
PREPARE TRANSACTION 'global_tx_branch_pg_01';

-- 3. Перегляд списку підвислих (In-Doubt) транзакцій (аналог xa_recover)
SELECT gid, prepared, owner, database FROM pg_prepared_xacts;

-- 4. Фаза 2: остаточна фіксація або відкат (аналог xa_commit / xa_rollback)
COMMIT PREPARED 'global_tx_branch_pg_01';
-- або у разі відкату:
ROLLBACK PREPARED 'global_tx_branch_pg_01';
