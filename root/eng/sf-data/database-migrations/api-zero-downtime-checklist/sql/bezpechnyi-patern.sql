-- 1. Створення окремої таблиці секції
CREATE TABLE logs_2026_08 (LIKE logs INCLUDING ALL);

-- 2. Додавання перевірочного обмеження CHECK, що повністю покриває діапазон
ALTER TABLE logs_2026_08 ADD CONSTRAINT check_partition_bounds 
    CHECK (log_date >= '2026-08-01' AND log_date < '2026-09-01');

-- 3. Приєднання секції (миттєво, оскільки CHECK-обмеження гарантує валідність діапазону)
ALTER TABLE logs ATTACH PARTITION logs_2026_08 
    FOR VALUES FROM ('2026-08-01') TO ('2026-09-01');

-- 4. Видалення надлишкового обмеження CHECK після успішного приєднання
ALTER TABLE logs_2026_08 DROP CONSTRAINT check_partition_bounds;
