CREATE TYPE webhook_status AS ENUM ('pending', 'processing', 'delivered', 'failed', 'dead_letter');

CREATE TABLE outbox_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(64) NOT NULL,
    destination_url TEXT NOT NULL,
    secret_key VARCHAR(128) NOT NULL,
    event_type VARCHAR(64) NOT NULL,
    payload JSONB NOT NULL,
    status webhook_status NOT NULL DEFAULT 'pending',
    attempts INT NOT NULL DEFAULT 0,
    max_attempts INT NOT NULL DEFAULT 10,
    next_retry_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    locked_by VARCHAR(64),
    locked_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Частковий індекс для швидкої вибірки лише тих подій, що готові до відправки
CREATE INDEX idx_outbox_poll ON outbox_events (next_retry_at, status) 
WHERE status IN ('pending', 'failed');

-- Таблиця аудиту спроб доставки для діагностики та надання логів користувачам
CREATE TABLE delivery_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id UUID NOT NULL REFERENCES outbox_events(id) ON DELETE CASCADE,
    attempt_number INT NOT NULL,
    response_status INT,
    response_body TEXT,
    duration_ms INT NOT NULL,
    error_message TEXT,
    attempted_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_attempts_event ON delivery_attempts (event_id);
