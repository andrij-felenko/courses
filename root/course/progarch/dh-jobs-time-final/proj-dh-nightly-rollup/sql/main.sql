CREATE TABLE daily_summary (
  home_id     text    NOT NULL,
  day         date    NOT NULL,             -- ЛОКАЛЬНА доба дому, НЕ UTC-мить
  kwh         numeric NOT NULL,
  peak_w      numeric NOT NULL,
  samples     integer NOT NULL,
  zone        text    NOT NULL,             -- зона розрахунку (для аудиту)
  computed_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (home_id, day)                -- ← сам ключ ідемпотентності
);

INSERT INTO daily_summary (home_id, day, kwh, peak_w, samples, zone)
VALUES ($1, $2, $3, $4, $5, $6)
ON CONFLICT (home_id, day) DO UPDATE         -- другий запуск ПЕРЕПИШЕ, а не додасть
   SET kwh = EXCLUDED.kwh, peak_w = EXCLUDED.peak_w,
       samples = EXCLUDED.samples, computed_at = now();
