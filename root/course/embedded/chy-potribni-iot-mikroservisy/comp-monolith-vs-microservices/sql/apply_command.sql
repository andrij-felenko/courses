-- Операція «встановити граничний струм 32 А та режим Автоматичний» цілком.
-- Чотири кроки з прози — права, конфігурація, аудит із тарифікацією, черга
-- вихідних команд — виконуються в одній транзакції однієї бази. Будь-яка
-- невдача піднімає виняток, і база відкочує ВСЕ: компенсуючі транзакції,
-- оркестратор саг і ідемпотентні повтори між сервісами тут просто не потрібні.

CREATE OR REPLACE FUNCTION apply_device_command(
    p_user_id     bigint,
    p_device_id   text,
    p_max_current numeric,
    p_mode        text,
    p_idem_key    text
) RETURNS bigint
LANGUAGE plpgsql
AS $$
DECLARE
    v_hw_limit numeric;
    v_prev     numeric;   -- чинний ліміт, іде в аудит
    v_cmd_id   bigint;
BEGIN
    -- 1. Права користувача + апаратні межі пристрою.
    --    FOR UPDATE OF d тримає рядок пристрою до кінця транзакції: дві
    --    паралельні команди на той самий вузол вишикуються в чергу, а не
    --    переганяють одна одну (у мікросервісах це вже гонитва в Redis).
    SELECT d.hw_max_current, c.max_current
      INTO v_hw_limit, v_prev
      FROM devices d
      JOIN device_grants  g ON g.device_id = d.id AND g.user_id = p_user_id
      LEFT JOIN device_configs c ON c.device_id = d.id
     WHERE d.id = p_device_id
       AND g.can_control
     FOR UPDATE OF d;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'користувач % не керує пристроєм %', p_user_id, p_device_id
            USING ERRCODE = 'insufficient_privilege';
    END IF;

    IF v_prev IS NULL THEN
        RAISE EXCEPTION 'у пристрою % нема конфігурації', p_device_id
            USING ERRCODE = 'no_data_found';
    END IF;

    IF p_max_current > v_hw_limit THEN
        RAISE EXCEPTION 'ліміт % А перевищує апаратну межу % А пристрою %',
                        p_max_current, v_hw_limit, p_device_id
            USING ERRCODE = 'check_violation';
    END IF;

    -- Повтор тієї самої команди (клієнт не дочекався відповіді й натиснув ще
    -- раз) не має ні списати гроші вдруге, ні покласти в чергу другий пакет.
    SELECT id INTO v_cmd_id FROM outbound_commands WHERE idem_key = p_idem_key;
    IF FOUND THEN
        RETURN v_cmd_id;
    END IF;

    -- 2. Бажаний стан у реєстрі. Рядок пристрою заблокований вище, тож
    --    конфігурація нікуди не зникне між перевіркою і записом.
    UPDATE device_configs
       SET max_current = p_max_current,
           mode        = p_mode,
           revision    = revision + 1,
           updated_at  = now()
     WHERE device_id = p_device_id;

    -- 3. Аудит і тарифікаційна подія.
    INSERT INTO audit_logs (device_id, user_id, action, details)
    VALUES (p_device_id, p_user_id, 'SET_LIMIT',
            jsonb_build_object('from', v_prev, 'to', p_max_current, 'mode', p_mode));

    INSERT INTO billing_events (user_id, device_id, sku, amount_cents, idem_key)
    VALUES (p_user_id, p_device_id, 'device.command', 5, p_idem_key);

    -- 4. Черга вихідних повідомлень. Публікує в MQTT окремий диспетчер
    --    (див. outbox_dispatch.sql) — це єдине місце, де транзакційна
    --    гарантія закінчується і починається мережа.
    INSERT INTO outbound_commands (device_id, topic, payload, idem_key)
    VALUES (p_device_id,
            format('devices/%s/cmd', p_device_id),
            jsonb_build_object('cmd', 'set_limit',
                               'val', p_max_current,
                               'mode', p_mode),
            p_idem_key)
    RETURNING id INTO v_cmd_id;

    RETURN v_cmd_id;
END;
$$;

-- Виклик із застосунку: один мережевий стрибок до бази замість чотирьох
-- міжсервісних. Виняток усередині функції відкочує транзакцію повністю.
BEGIN;
SELECT apply_device_command(17, 'node_1042', 32.0, 'auto',
                            'ui-7f3c-2026-08-29T10:12:04Z');
COMMIT;
