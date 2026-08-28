-- PostgreSQL DDL (Рекомендована промислова конфігурація)
CREATE TABLE inbox_messages (
    message_id       VARCHAR(128) NOT NULL,
    consumer_group   VARCHAR(64)  NOT NULL DEFAULT 'default',
    event_type       VARCHAR(128) NOT NULL,
    payload          JSONB        NOT NULL,
    status           VARCHAR(32)  NOT NULL DEFAULT 'RECEIVED',
    retry_count      INTEGER      NOT NULL DEFAULT 0,
    max_retries      INTEGER      NOT NULL DEFAULT 5,
    last_error       TEXT,
    locked_until     TIMESTAMPTZ,
    locked_by        VARCHAR(64),
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    processed_at     TIMESTAMPTZ,
    PRIMARY KEY (message_id, consumer_group),
    CONSTRAINT chk_inbox_status CHECK (status IN ('RECEIVED', 'PROCESSING', 'PROCESSED', 'FAILED'))
);

-- Частковий індекс для конкурентної вибірки активних завдань воркерами
CREATE INDEX idx_inbox_active_polling 
ON inbox_messages (consumer_group, created_at) 
WHERE status IN ('RECEIVED', 'PROCESSING');

-- Частковий індекс для фонового процесу очищення (TTL Pruning)
CREATE INDEX idx_inbox_processed_cleanup 
ON inbox_messages (processed_at) 
WHERE status = 'PROCESSED';
