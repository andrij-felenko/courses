-- 1. Базово партиційована таблиця пристроїв за значенням tenant_id
CREATE TABLE devices_partitioned (
    id UUID DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(64) NOT NULL,
    name VARCHAR(128) NOT NULL,
    status VARCHAR(32) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT clock_timestamp(),
    PRIMARY KEY (tenant_id, id)
) PARTITION BY LIST (tenant_id);

-- 2. Створення окремих партицій для великих орендарів або пулу дрібних
CREATE TABLE devices_tenant_101 PARTITION OF devices_partitioned
    FOR VALUES IN ('tenant_101');

CREATE TABLE devices_tenant_102 PARTITION OF devices_partitioned
    FOR VALUES IN ('tenant_102');

-- 3. Вмикаємо RLS на базі партиційованої таблиці
ALTER TABLE devices_partitioned ENABLE ROW LEVEL SECURITY;
ALTER TABLE devices_partitioned FORCE ROW LEVEL SECURITY;

CREATE POLICY tenant_partition_policy ON devices_partitioned
    FOR ALL
    TO app_user
    USING (tenant_id = current_setting('app.current_tenant', true))
    WITH CHECK (tenant_id = current_setting('app.current_tenant', true));
