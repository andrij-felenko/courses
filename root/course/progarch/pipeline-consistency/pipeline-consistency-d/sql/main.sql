-- ❌ Наївно: кожна доставка додає до лічника.
--    Повтор → те саме число додалося двічі → переоблік.
UPDATE daily_energy SET kwh = kwh + 0.4
WHERE home_id = :home AND day = :day;

-- ✅ Ідемпотентно: запис за стабільним ключем (лічильник, час).
--    Повтор перезаписує той самий рядок тим самим значенням → но-оп.
INSERT INTO reading (meter_id, ts, kwh)
VALUES (:meter, :ts, 0.4)
ON CONFLICT (meter_id, ts) DO UPDATE SET kwh = EXCLUDED.kwh;
