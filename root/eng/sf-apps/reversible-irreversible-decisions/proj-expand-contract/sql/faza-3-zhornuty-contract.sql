-- 3a. Розвернути синхронізацію: тепер джерело правди — amount_minor,
--     а стара total лишається дійсною (виводиться), щоб відкат був можливий
--     аж до самого DROP. Нову колонку робимо обов'язковою — і цей крок
--     САМ перевіряє повноту backfill: якщо є хоч один NULL, він упаде.
ALTER TABLE orders ALTER COLUMN amount_minor SET NOT NULL;

CREATE OR REPLACE FUNCTION sync_amount_minor() RETURNS trigger AS $$
BEGIN
    NEW.total := NEW.amount_minor / 100.0;   -- зворотний напрям: копійки → гривні
    RETURN NEW;
END $$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_sync_amount_minor ON orders;
CREATE TRIGGER trg_sync_amount_minor
    BEFORE INSERT OR UPDATE OF amount_minor ON orders
    FOR EACH ROW EXECUTE FUNCTION sync_amount_minor();
