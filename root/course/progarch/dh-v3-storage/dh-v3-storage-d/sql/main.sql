-- Реєстр і конфіг: джерело правди дому. Нудні реляційні таблиці.
CREATE TABLE home (
    id          TEXT PRIMARY KEY,
    owner_id    TEXT    NOT NULL,
    plan        TEXT    NOT NULL DEFAULT 'free',   -- тариф
    device_cap  INTEGER NOT NULL DEFAULT 5,        -- межа слотів пристроїв
    used_slots  INTEGER NOT NULL DEFAULT 0,        -- скільки зайнято
    threshold   REAL    NOT NULL DEFAULT 20.0      -- поріг опалення (Config з v2)
);

CREATE TABLE device (
    id          TEXT PRIMARY KEY,
    home_id     TEXT NOT NULL REFERENCES home(id) ON DELETE CASCADE,  -- зовнішній ключ
    kind        TEXT NOT NULL,              -- lock | thermostat | plug
    room        TEXT NOT NULL,
    state       TEXT NOT NULL,
    paired_at   TEXT NOT NULL,
    UNIQUE (id)                             -- один фізичний давач — один рядок
);
