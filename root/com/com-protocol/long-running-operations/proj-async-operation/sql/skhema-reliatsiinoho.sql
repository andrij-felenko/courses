CREATE TABLE operations (
    id                  VARCHAR(36) PRIMARY KEY,
    owner_id            VARCHAR(64) NOT NULL,
    kind                VARCHAR(64) NOT NULL,
    payload_hash        BYTEA NOT NULL,
    priority            SMALLINT NOT NULL DEFAULT 100,
    state               VARCHAR(16) NOT NULL DEFAULT 'pending'
                        CHECK (state IN ('pending', 'running', 'succeeded', 'failed', 'cancelled')),
    progress            REAL NOT NULL DEFAULT 0.0
                        CHECK (progress >= 0.0 AND progress <= 1.0),
    stage               VARCHAR(64) NOT NULL DEFAULT 'queued',
    checkpoint_data     JSONB,
    result_url          VARCHAR(512),
    error_details       JSONB,
    cancel_requested    BOOLEAN NOT NULL DEFAULT FALSE,
    attempt             INTEGER NOT NULL DEFAULT 0,
    lease_token         UUID,
    lease_until         TIMESTAMPTZ,
    idempotency_key     VARCHAR(128),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at          TIMESTAMPTZ NOT NULL
);

-- Унікальний індекс ідемпотентності: захищає від дублювання операцій
CREATE UNIQUE INDEX idx_operations_idempotency 
    ON operations (owner_id, idempotency_key)
 WHERE idempotency_key IS NOT NULL;

-- Часткові індекси для високошвидкісної черги воркерів
CREATE INDEX idx_operations_pending_queue 
    ON operations (priority DESC, created_at ASC)
 WHERE state = 'pending';

CREATE INDEX idx_operations_expired_leases 
    ON operations (lease_until)
 WHERE state = 'running';
