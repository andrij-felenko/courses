-- 1. Створення таблиці рахунків-фактур
CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(64) NOT NULL,
    amount NUMERIC(12, 2) NOT NULL,
    customer_email TEXT NOT NULL
);

-- 2. Активація обов'язкового RLS
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoices FORCE ROW LEVEL SECURITY;

-- 3. Декларація політики: доступ лише до рядків із власним tenant_id
CREATE POLICY tenant_isolation_invoices ON invoices
    FOR ALL
    USING (tenant_id = current_setting('app.current_tenant_id', true))
    WITH CHECK (tenant_id = current_setting('app.current_tenant_id', true));
