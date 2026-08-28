-- ✓ межі порахував застосунок; над колонкою немає жодного виразу
SELECT count(*) FROM reminder
 WHERE user_id = $1
   AND fire_at >= $2       -- 2026-10-24 21:00:00+00
   AND fire_at <  $3;      -- 2026-10-25 22:00:00+00

-- ✗ вираз над колонкою: значення треба порахувати для кожного рядка таблиці
SELECT count(*) FROM reminder
 WHERE user_id = $1
   AND (fire_at AT TIME ZONE 'Europe/Kyiv')::date = DATE '2026-10-25';
