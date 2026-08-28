-- РЕЄСТР: джерело правди дому. Корінь агрегату.
CREATE TABLE home (
    id          TEXT PRIMARY KEY,
    owner_id    TEXT    NOT NULL,
    plan        TEXT    NOT NULL DEFAULT 'free',              -- тариф
    device_cap  INTEGER NOT NULL DEFAULT 5,                   -- скільки слотів дає тариф
    used_slots  INTEGER NOT NULL DEFAULT 0 CHECK (used_slots >= 0),
    threshold   REAL    NOT NULL DEFAULT 20.0,                -- поріг опалення
    CHECK (used_slots <= device_cap)                          -- лічильник НЕ переростає межу
);

-- ПРИСТРІЙ: дитина агрегату. Живе й зберігається разом із коренем.
CREATE TABLE device (
    id         TEXT PRIMARY KEY,                              -- один фізичний давач — один рядок
    home_id    TEXT NOT NULL REFERENCES home(id) ON DELETE CASCADE,   -- сирота неможливий
    kind       TEXT NOT NULL CHECK (kind IN ('lock','thermostat','plug','sensor')),
    room       TEXT NOT NULL,
    state      TEXT NOT NULL,
    paired_at  TEXT NOT NULL
);

-- ТЕЛЕМЕТРІЯ: інша природа запису. ПОЗА агрегатом реєстру.
CREATE TABLE measurement (
    device_id  TEXT NOT NULL,
    ts         REAL NOT NULL,
    value      REAL NOT NULL,
    PRIMARY KEY (device_id, ts)                               -- один показ на давач у мить
);
