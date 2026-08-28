-- 1. Початок гілки транзакції (xa_start)
XA START 'global_tx_001', 'mysql_branch_01';
UPDATE warehouse SET items_count = items_count - 1 WHERE item_id = 42;
XA END 'global_tx_001', 'mysql_branch_01';

-- 2. Фаза 1: підготовка (xa_prepare)
XA PREPARE 'global_tx_001', 'mysql_branch_01';

-- 3. Моніторинг нефіксованих транзакцій (xa_recover)
XA RECOVER;

-- 4. Фаза 2: коміт (xa_commit)
XA COMMIT 'global_tx_001', 'mysql_branch_01';
