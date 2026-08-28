-- Синхронізація на час переходу: похідну колонку веде сама база.
-- Джерело правди поки що — total; amount_minor щоразу виводиться з нього.
CREATE FUNCTION sync_amount_minor() RETURNS trigger AS $$
BEGIN
    NEW.amount_minor := ROUND(NEW.total * 100)::BIGINT;   -- гривні → копійки, точно
    RETURN NEW;
END $$ LANGUAGE plpgsql;

CREATE TRIGGER trg_sync_amount_minor
    BEFORE INSERT OR UPDATE OF total ON orders
    FOR EACH ROW EXECUTE FUNCTION sync_amount_minor();
