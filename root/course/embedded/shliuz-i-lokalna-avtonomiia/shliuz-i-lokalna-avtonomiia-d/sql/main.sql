CREATE TABLE IF NOT EXISTS outbound_queue (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at  INTEGER NOT NULL,     -- Мітка часу зняття вимірювання (UNIX ms)
    priority    INTEGER NOT NULL,     -- 0: Телеметрія, 1: Стан/Події, 2: Аварії (Alarms)
    topic       TEXT NOT NULL,        -- Цільовий MQTT-топік
    payload     BLOB NOT NULL,        -- Бінарний payload (JSON / CBOR / Protobuf)
    status      INTEGER DEFAULT 0     -- 0: PENDING, 1: IN_FLIGHT
);

CREATE INDEX IF NOT EXISTS idx_queue_drain 
ON outbound_queue (status, priority DESC, id ASC);
