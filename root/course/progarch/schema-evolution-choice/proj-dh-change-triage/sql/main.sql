-- ✓ безкоштовно: nullable, без дефолта → лише метадані, жодного рерайту рядків
ALTER TABLE home ADD COLUMN firmware_channel text;   -- старі рядки = NULL = «невідомо»

-- ❌ тиха брехня: NOT NULL з дефолтом насаджує старим рядкам сенс, якого вони не мали
ALTER TABLE home ADD COLUMN firmware_channel text NOT NULL DEFAULT 'stable';
--   PostgreSQL 11+ зробить це теж швидко (сталий дефолт — лише метадані),
--   АЛЕ кожен старий рядок відтепер СТВЕРДЖУЄ, що він 'stable' — хоч канал невідомий;
--   NULL «ми не знали» тихо став 'stable' — і ти вже не відрізниш знаних від незнаних.

-- ❌❌ і зовсім дорого — зробити поле обов'язковим ПІЗНІШЕ:
ALTER TABLE home ALTER COLUMN firmware_channel SET NOT NULL;
--   повний скан таблиці під ACCESS EXCLUSIVE, щоб довести, що NULL-ів нема → лок на весь скан
