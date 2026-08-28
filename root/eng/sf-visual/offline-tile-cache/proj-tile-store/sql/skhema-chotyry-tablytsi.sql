CREATE TABLE IF NOT EXISTS tiles (
  key     INTEGER PRIMARY KEY,   -- (джерело, z, x, y), запаковані в 61 біт
  bytes   INTEGER NOT NULL,      -- довжина тіла; 0 разом із body IS NULL = «тайла немає»
  fetched INTEGER NOT NULL,      -- коли завантажено (unix-час)
  used    INTEGER NOT NULL,      -- коли востаннє віддано — за цим витісняємо
  etag    TEXT,                  -- мітка версії від сервера
  body    BLOB                   -- САМЕ ОСТАННІЙ стовпець, див. нижче
);
CREATE INDEX IF NOT EXISTS tiles_used ON tiles(used, bytes);

CREATE TABLE IF NOT EXISTS sets (
  id      INTEGER PRIMARY KEY,
  name    TEXT NOT NULL UNIQUE,
  src     INTEGER NOT NULL,
  zmin    INTEGER NOT NULL, zmax  INTEGER NOT NULL,
  west    REAL NOT NULL,    south REAL NOT NULL,
  east    REAL NOT NULL,    north REAL NOT NULL,
  created INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS set_tiles (       -- «набір посилається на тайл»
  set_id INTEGER NOT NULL REFERENCES sets(id) ON DELETE CASCADE,
  key    INTEGER NOT NULL,
  PRIMARY KEY (set_id, key)
) WITHOUT ROWID;
CREATE INDEX IF NOT EXISTS set_tiles_key ON set_tiles(key);

CREATE TABLE IF NOT EXISTS download_queue (  -- робота, що переживає перезапуск
  key    INTEGER NOT NULL,
  set_id INTEGER NOT NULL REFERENCES sets(id) ON DELETE CASCADE,
  state  INTEGER NOT NULL DEFAULT 0,         -- 0 чекає · 1 у роботі · 2 готово · 3 помилка
  tries  INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (set_id, key)
) WITHOUT ROWID;
CREATE INDEX IF NOT EXISTS queue_ready ON download_queue(state, set_id);
