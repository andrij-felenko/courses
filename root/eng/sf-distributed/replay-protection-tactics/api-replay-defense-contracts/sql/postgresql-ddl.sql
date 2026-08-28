-- Перелік статусів життєвого циклу обробки повідомлення
CREATE TYPE inbox_status AS ENUM ('PROCESSING', 'PROCESSED', 'FAILED');

-- Головна таблиця вхідних повідомлень із Range-секціонуванням за датою створення
CREATE TABLE inbox_messages (
    idempotency_key   VARCHAR(64)  NOT NULL,
    consumer_group    VARCHAR(64)  NOT NULL,
    source_event_id   VARCHAR(64)  NOT NULL,
    fencing_token     BIGINT       NOT NULL DEFAULT 0,
    status            inbox_status NOT NULL DEFAULT 'PROCESSING',
    response_payload  JSONB        NULL,
    response_status   INT          NULL,
    error_message     TEXT         NULL,
    created_at        TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    PRIMARY KEY (created_at, consumer_group, idempotency_key)
) PARTITION BY RANGE (created_at);

-- Добові секції (приклад автоматичного або ручного створення)
CREATE TABLE inbox_messages_2026_08_20 PARTITION OF inbox_messages
    FOR VALUES FROM ('2026-08-20 00:00:00+00') TO ('2026-08-21 00:00:00+00');

CREATE TABLE inbox_messages_2026_08_21 PARTITION OF inbox_messages
    FOR VALUES FROM ('2026-08-21 00:00:00+00') TO ('2026-08-22 00:00:00+00');

-- Індекс для миттєвої перевірки дублікатів у межах групи споживачів
CREATE INDEX idx_inbox_consumer_lookup 
    ON inbox_messages (consumer_group, idempotency_key);
