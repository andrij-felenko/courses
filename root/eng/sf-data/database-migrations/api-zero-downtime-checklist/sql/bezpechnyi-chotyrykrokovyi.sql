-- Крок 1: Додавання перевірочного обмеження без валідації (миттєве оновлення метаданих)
ALTER TABLE users ADD CONSTRAINT check_email_not_null CHECK (email IS NOT NULL) NOT VALID;

-- Крок 2: Валідація накопичених даних у фоновому режимі (ShareUpdateExclusiveLock, запис відкритий!)
ALTER TABLE users VALIDATE CONSTRAINT check_email_not_null;

-- Крок 3: Встановлення справжнього NOT NULL (миттєво, бо перевірку вже підтверджено обмеженням)
ALTER TABLE users ALTER COLUMN email SET NOT NULL;

-- Крок 4: Видалення тепер уже надлишкового обмеження CHECK
ALTER TABLE users DROP CONSTRAINT check_email_not_null;
