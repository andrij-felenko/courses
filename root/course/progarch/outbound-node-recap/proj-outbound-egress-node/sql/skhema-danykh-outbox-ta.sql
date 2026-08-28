-- Таблиця для збереження намірів вихідних відправок
CREATE TABLE outbound_outbox (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    destination_type VARCHAR(32) NOT NULL, -- WEBHOOK, PUSH, SMS, API
    destination_url TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    secret_key TEXT NOT NULL,
    idempotency_key VARCHAR(128) NOT NULL,
    status VARCHAR(16) NOT NULL DEFAULT 'PENDING', -- PENDING, PROCESSING, SENT, FAILED, DEAD_LETTER
    attempt INT NOT NULL DEFAULT 0,
    max_attempts INT NOT NULL DEFAULT 5,
    next_retry_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_error TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Частковий індекс для миттєвої вибірки робітниками готових до відправки задач
CREATE INDEX idx_outbox_processing 
ON outbound_outbox (status, next_retry_at) 
WHERE status IN ('PENDING', 'FAILED');

-- Індекс для швидкої дедуплікації за idempotency_key
CREATE UNIQUE INDEX idx_outbox_idempotency 
ON outbound_outbox (idempotency_key);
