-- SQLite DDL (для вбудованих застосунків та крайових вузлів)
CREATE TABLE inbox_messages (
    message_id       TEXT NOT NULL,
    consumer_group   TEXT NOT NULL DEFAULT 'default',
    event_type       TEXT NOT NULL,
    payload          TEXT NOT NULL,
    status           TEXT NOT NULL CHECK(status IN ('RECEIVED', 'PROCESSING', 'PROCESSED', 'FAILED')),
    retry_count      INTEGER NOT NULL DEFAULT 0,
    max_retries      INTEGER NOT NULL DEFAULT 5,
    last_error       TEXT,
    locked_until     INTEGER, -- Час у мілісекундах Epoch Unix
    locked_by        TEXT,
    created_at       INTEGER NOT NULL,
    processed_at     INTEGER,
    PRIMARY KEY (message_id, consumer_group)
);

CREATE INDEX idx_inbox_polling ON inbox_messages (consumer_group, status, locked_until);
CREATE INDEX idx_inbox_cleanup ON inbox_messages (processed_at);
