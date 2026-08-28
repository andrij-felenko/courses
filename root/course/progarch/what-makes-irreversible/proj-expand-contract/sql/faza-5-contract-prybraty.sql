-- ФАЗА 5 (contract) — ЛИШЕ коли нове відлежалося в проді, звірка тримає нуль
-- розбіжностей, а читачі давно на новому.

-- Крок 1. Закріплюємо NOT NULL БЕЗ повного замка на запис:
--   NOT VALID — миттєво, перевіряє лише нові рядки;
--   VALIDATE — сканує старі під м'яким замком (читання й запис не блокує).
ALTER TABLE readings ADD CONSTRAINT temp_mc_nn CHECK (temp_mc IS NOT NULL) NOT VALID;
ALTER TABLE readings VALIDATE CONSTRAINT temp_mc_nn;

-- Крок 2. Єдина незворотна дія — прибрати старе. Тому вона тут, останньою,
--   і тільки після всього попереднього. Оце й є та однобічна двер.
ALTER TABLE readings DROP COLUMN temp_c;
