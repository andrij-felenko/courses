-- ФАЗА 1 · EXPAND: додаємо нову форму поруч; стару не чіпаємо.
ALTER TABLE home ADD COLUMN tariff_zone smallint;   -- NULL, поки не заповнено
-- застосунок віднині пише В ОБИДВА поля (zone і tariff_zone),
-- а читає поки що зі старого zone — жоден читач не зламався.

-- ФАЗА 2 · MIGRATE: backfill старих рядків пакетами, щоб не лочити всю таблицю.
UPDATE home SET tariff_zone = zone_to_code(zone)
WHERE tariff_zone IS NULL AND id BETWEEN :lo AND :hi;   -- ганяємо по діапазонах ключа
-- коли всі рядки заповнено — переводимо читачів на tariff_zone (реліз за релізом).

-- ФАЗА 3 · CONTRACT: ніхто не читає zone — прибираємо стару форму.
ALTER TABLE home DROP COLUMN zone;
