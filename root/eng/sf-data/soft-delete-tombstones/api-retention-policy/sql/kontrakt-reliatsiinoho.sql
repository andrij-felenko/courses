-- 1. Увімкнення механізму безпеки на рівні рядків для цільової таблиці
ALTER TABLE accounts ENABLE ROW LEVEL SECURITY;

-- За замовчуванням власник таблиці та суперкористувач ігнорують RLS. 
-- Команда FORCE гарантує, що політики застосовуватимуться навіть до власника схеми,
-- що унеможливлює випадкове виконання скриптів без урахування м'якого видалення.
ALTER TABLE accounts FORCE ROW LEVEL SECURITY;

-- 2. Політика для стандартних користувачів та бізнес-сервісів (видимі лише активні рядки)
-- Конструкція USING фільтрує читання (SELECT), а WITH CHECK забороняє створення або 
-- модифікацію рядків, які не відповідають критерію живого запису.
CREATE POLICY active_records_only ON accounts
    FOR ALL
    TO application_user
    USING (deleted_at IS NULL)
    WITH CHECK (deleted_at IS NULL);

-- 3. Політика для аудиторів та фонового сервісу очищення (повний доступ до всіх рядків)
CREATE POLICY audit_and_purge_access ON accounts
    FOR ALL
    TO purge_daemon_user, compliance_auditor
    USING (TRUE)
    WITH CHECK (TRUE);
