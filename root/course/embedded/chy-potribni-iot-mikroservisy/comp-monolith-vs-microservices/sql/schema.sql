-- Реєстр пристроїв модульного моноліту: одна база PostgreSQL на всі модулі.
-- Саме тому чотири кроки операції з прози вкладаються в ОДНУ транзакцію:
-- права, конфігурація, аудит, тарифікація і черга вихідних команд лежать
-- у тому самому екземплярі бази, а не в чотирьох різних сервісах.

CREATE TABLE users (
    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    login       text        NOT NULL UNIQUE,
    created_at  timestamptz NOT NULL DEFAULT now()
);

-- Фізичний пристрій. hw_max_current — апаратна межа плати: скільки б
-- користувач не просив, більше за неї виставити не можна.
CREATE TABLE devices (
    id             text        PRIMARY KEY,
    model          text        NOT NULL,
    hw_max_current numeric(6,2) NOT NULL CHECK (hw_max_current > 0),
    firmware_ver   text        NOT NULL,
    state          text        NOT NULL DEFAULT 'offline'
                   CHECK (state IN ('online', 'offline', 'fault')),
    last_seen      timestamptz
);

-- Хто чим має право керувати. У мікросервісній схемі це окремий Auth Service
-- і ще один мережевий стрибок; тут — звичайний JOIN у тій самій транзакції.
CREATE TABLE device_grants (
    user_id     bigint  NOT NULL REFERENCES users(id)   ON DELETE CASCADE,
    device_id   text    NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    can_control boolean NOT NULL DEFAULT false,
    PRIMARY KEY (user_id, device_id)
);

-- Бажаний стан (Desired State). Реальний стан приходить з пристрою окремо;
-- revision росте на кожну зміну, щоб прошивка бачила, чи вона відстала.
CREATE TABLE device_configs (
    device_id   text         PRIMARY KEY REFERENCES devices(id) ON DELETE CASCADE,
    max_current numeric(6,2) NOT NULL CHECK (max_current > 0),
    mode        text         NOT NULL CHECK (mode IN ('manual', 'auto', 'off')),
    revision    integer      NOT NULL DEFAULT 1,
    updated_at  timestamptz  NOT NULL DEFAULT now()
);

CREATE TABLE audit_logs (
    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    device_id   text        NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    user_id     bigint      NOT NULL REFERENCES users(id),
    action      text        NOT NULL,
    details     jsonb       NOT NULL DEFAULT '{}'::jsonb,
    at          timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX audit_logs_device_at_idx ON audit_logs (device_id, at DESC);

-- Тарифікаційна подія. idem_key унікальний: повтор тієї самої команди
-- не спишe гроші вдруге навіть тоді, коли клієнт не дочекався відповіді.
CREATE TABLE billing_events (
    id           bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id      bigint      NOT NULL REFERENCES users(id),
    device_id    text        NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    sku          text        NOT NULL,
    amount_cents integer     NOT NULL CHECK (amount_cents > 0),
    idem_key     text        NOT NULL UNIQUE,
    at           timestamptz NOT NULL DEFAULT now()
);

-- Transactional Outbox: команда для MQTT лягає в базу тією ж транзакцією,
-- що й конфігурація. Або є обидва записи, або нема жодного — розсинхронізації
-- «в базі 32 А, пристрій живе на 16 А» тут не існує.
CREATE TABLE outbound_commands (
    id         bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    device_id  text        NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    topic      text        NOT NULL,
    payload    jsonb       NOT NULL,
    idem_key   text        NOT NULL UNIQUE,
    attempts   integer     NOT NULL DEFAULT 0,
    created_at timestamptz NOT NULL DEFAULT now(),
    sent_at    timestamptz
);

-- Частковий індекс: диспетчер черги сканує лише невідправлені рядки,
-- а не всю історію команд.
CREATE INDEX outbound_commands_pending_idx
    ON outbound_commands (id)
    WHERE sent_at IS NULL;
