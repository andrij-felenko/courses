CREATE TABLE outbox_messages (
    id              BIGSERIAL PRIMARY KEY,
    aggregate_type  VARCHAR(64) NOT NULL,      -- 'DeviceTwin'
    aggregate_id    VARCHAR(64) NOT NULL,      -- 'lock_front_door'
    event_type      VARCHAR(64) NOT NULL,      -- 'LockUnlockCommanded'
    payload         JSONB NOT NULL,            -- Тіло команди
    trace_id        VARCHAR(32) NOT NULL,      -- W3C Trace ID
    span_id         VARCHAR(16) NOT NULL,      -- W3C Span ID
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    processed_at    TIMESTAMPTZ NULL,          -- NULL доки CDC / Relay не відправив у Kafka
    retry_count     INT NOT NULL DEFAULT 0
);

CREATE INDEX idx_outbox_unprocessed ON outbox_messages (created_at) WHERE processed_at IS NULL;
