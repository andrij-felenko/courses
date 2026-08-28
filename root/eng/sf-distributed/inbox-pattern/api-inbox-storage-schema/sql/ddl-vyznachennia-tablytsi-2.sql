-- MySQL 8.0+ DDL (з підтримкою InnoDB та JSON)
CREATE TABLE inbox_messages (
    message_id       VARCHAR(128) NOT NULL,
    consumer_group   VARCHAR(64)  NOT NULL DEFAULT 'default',
    event_type       VARCHAR(128) NOT NULL,
    payload          JSON         NOT NULL,
    status           VARCHAR(32)  NOT NULL DEFAULT 'RECEIVED',
    retry_count      INT          NOT NULL DEFAULT 0,
    max_retries      INT          NOT NULL DEFAULT 5,
    last_error       TEXT,
    locked_until     DATETIME(6)  NULL,
    locked_by        VARCHAR(64)  NULL,
    created_at       DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    processed_at     DATETIME(6)  NULL,
    PRIMARY KEY (message_id, consumer_group),
    INDEX idx_inbox_polling (consumer_group, status, locked_until, created_at),
    INDEX idx_inbox_cleanup (processed_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
