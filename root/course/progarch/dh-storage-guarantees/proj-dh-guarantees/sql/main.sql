-- РЕЄСТР: джерело правди про дім. Кожне обмеження — це «ні», яке база каже замість нас.
CREATE TABLE IF NOT EXISTS homes (
  id         TEXT PRIMARY KEY,                       -- один дім — один рядок
  owner      TEXT NOT NULL,
  threshold  REAL    NOT NULL CHECK (threshold BETWEEN 5 AND 35),   -- поріг у людських межах
  heat_left  INTEGER NOT NULL CHECK (heat_left >= 0)                 -- бюджет нагріву, хвилини
);

CREATE TABLE IF NOT EXISTS devices (
  home_id  TEXT NOT NULL,
  id       TEXT NOT NULL,
  kind     TEXT NOT NULL CHECK (kind IN ('lock','plug','thermostat','sensor')),
  room     TEXT,
  PRIMARY KEY (home_id, id),                          -- один пристрій — один запис у домі
  UNIQUE (id),                                        -- давач не належить двом домам ОДНОЧАСНО
  FOREIGN KEY (home_id) REFERENCES homes(id) ON DELETE CASCADE   -- пристрій-сирота неможливий
);

-- ТЕЛЕМЕТРІЯ: лавина показів. Жодного обмеження понад PRIMARY KEY — рядки не сперечаються.
CREATE TABLE IF NOT EXISTS telemetry (
  seq     INTEGER PRIMARY KEY,      -- монотонний rowid, база веде його сама
  device  TEXT NOT NULL,
  ts      REAL NOT NULL,
  value   REAL NOT NULL
);
