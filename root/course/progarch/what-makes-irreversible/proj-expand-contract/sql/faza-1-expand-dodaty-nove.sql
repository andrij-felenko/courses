-- ❌ Пастки фази 1 — усе це однобічні двері, не роби їх тут:

-- (1) зміна типу на місці — той самий перезапис усієї таблиці під ACCESS
--     EXCLUSIVE, з якого ми й тікаємо.
ALTER TABLE readings ALTER COLUMN temp_c TYPE bigint USING round(temp_c*1000);

-- (2) перейменування колонки — миттєве, але старий код, що читає temp_c,
--     ламається В ТУ Ж СЕКУНДУ: немає фази співіснування, немає відкату.
ALTER TABLE readings RENAME COLUMN temp_c TO temp_mc;

-- (3) одразу NOT NULL — на непорожній таблиці Postgres відмовить
--     («column contains null values»), бо старі рядки порожні; а якщо
--     продавити через DEFAULT-вираз, дістанеш перезапис. NOT NULL — аж
--     наприкінці, коли колонка вже заповнена (фаза 5).
ALTER TABLE readings ADD COLUMN temp_mc bigint NOT NULL;
