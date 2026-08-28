-- 1. Створення цільової таблиці зі стовпчиком орендаря
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(64) NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL
);

-- 2. Увімкнення механізму RLS
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- 3. Примусове застосування RLS навіть для власника таблиці (захист від обходу)
ALTER TABLE documents FORCE ROW LEVEL SECURITY;

-- 4. Створення політики повної ізоляції операцій читання та модифікації
CREATE POLICY tenant_isolation_policy ON documents
    FOR ALL
    USING (tenant_id = current_setting('app.current_tenant_id', true))
    WITH CHECK (tenant_id = current_setting('app.current_tenant_id', true));
