-- Інкрементна підтримка: кожен reading доливає СВІЙ Вт·год у рядок дня.
CREATE OR REPLACE FUNCTION bump_daily_energy() RETURNS trigger AS $$
BEGIN
  INSERT INTO daily_energy AS d (home_id, day, wh_sum, n_readings, computed_at)
  VALUES (NEW.home_id,
          (NEW.ts AT TIME ZONE 'Europe/Kyiv')::date,   -- день за ОДНИМ годинником
          NEW.wh, 1, now())
  ON CONFLICT (home_id, day) DO UPDATE
    SET wh_sum      = d.wh_sum + EXCLUDED.wh_sum,       -- доливаємо дельту
        n_readings  = d.n_readings + 1,
        computed_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_bump_daily
  AFTER INSERT ON reading
  FOR EACH ROW EXECUTE FUNCTION bump_daily_energy();
