-- Частковий унікальний індекс: гарантує унікальність email лише серед живих записів
CREATE UNIQUE INDEX idx_accounts_unique_active_email 
    ON accounts (email) 
    WHERE deleted_at IS NULL;

-- Частковий індекс для оптимізації фонового процесу очищення застарілих даних
-- Забезпечує миттєвий пошук кандидатів на фізичне видалення без сканування всієї таблиці
CREATE INDEX idx_accounts_retention_purge 
    ON accounts (deleted_at) 
    WHERE deleted_at IS NOT NULL;
