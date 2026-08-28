-- 1. Створення таблиці у фазі Expand (з новим NULLABLE полем tax_identifier)
ALTER TABLE customer_invoices 
ADD COLUMN tax_identifier VARCHAR(64) DEFAULT NULL;

-- 2. Функція тригера: якщо код v1 пише у старе поле tax_code, 
-- або код v2 пише у нове поле tax_identifier, обидва поля синхронізуються.
CREATE OR REPLACE FUNCTION sync_invoice_tax_fields()
RETURNS TRIGGER AS $$
BEGIN
    -- Якщо запис зроблено кодом v1 (заповнено лише tax_code)
    IF NEW.tax_code IS NOT NULL AND NEW.tax_identifier IS NULL THEN
        NEW.tax_identifier := NEW.tax_code;
    END IF;
    
    -- Якщо запис зроблено кодом v2 (заповнено лише tax_identifier)
    IF NEW.tax_identifier IS NOT NULL AND NEW.tax_code IS NULL THEN
        NEW.tax_code := NEW.tax_identifier;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 3. Прив'язка тригера до таблиці на етапі SCHEMA_EXPANDING
CREATE TRIGGER trg_sync_invoice_tax
BEFORE INSERT OR UPDATE ON customer_invoices
FOR EACH ROW EXECUTE FUNCTION sync_invoice_tax_fields();
