-- 1. Створення обмеженої ролі доступу для додатку (НЕ суперкористувача!)
CREATE ROLE app_user WITH LOGIN PASSWORD 'secure_password';

-- 2. Створення таблиці пристроїв із колонкою tenant_id
CREATE TABLE devices (
    id UUID DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(64) NOT NULL,
    name VARCHAR(128) NOT NULL,
    status VARCHAR(32) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT clock_timestamp(),
    PRIMARY KEY (tenant_id, id)
);

-- Надаємо права обмеженій ролі
GRANT SELECT, INSERT, UPDATE, DELETE ON devices TO app_user;

-- 3. Вмикаємо Row-Level Security для таблиці
ALTER TABLE devices ENABLE ROW LEVEL SECURITY;

-- 4. Примусове застосування RLS навіть для власника таблиці (FORCE RLS)
ALTER TABLE devices FORCE ROW LEVEL SECURITY;

-- 5. Створення політики доступу на основі сесійної змінної app.current_tenant
CREATE POLICY tenant_isolation_policy ON devices
    FOR ALL
    TO app_user
    USING (tenant_id = current_setting('app.current_tenant', true))
    WITH CHECK (tenant_id = current_setting('app.current_tenant', true));

-- 6. Допоміжний тригер: автоматично підставляє tenant_id із сесії, якщо додаток його не вказав
CREATE OR REPLACE FUNCTION set_tenant_id_from_session()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.tenant_id IS NULL OR NEW.tenant_id = '' THEN
        NEW.tenant_id := current_setting('app.current_tenant', false);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_set_tenant_id
    BEFORE INSERT ON devices
    FOR EACH ROW
    EXECUTE FUNCTION set_tenant_id_from_session();
