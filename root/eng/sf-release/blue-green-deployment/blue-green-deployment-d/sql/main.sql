-- Додаємо нові поля як опціональні (NULLable)
ALTER TABLE customers ADD COLUMN first_name VARCHAR(128);
ALTER TABLE customers ADD COLUMN last_name VARCHAR(128);

-- Створюємо тригер бази даних для автоматичного розщеплення full_name під час запису старим кодом v1
CREATE OR REPLACE FUNCTION sync_customer_names() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.first_name IS NULL THEN
        NEW.first_name := split_part(NEW.full_name, ' ', 1);
        NEW.last_name := split_part(NEW.full_name, ' ', 2);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_sync_names BEFORE INSERT OR UPDATE ON customers
FOR EACH ROW EXECUTE FUNCTION sync_customer_names();
