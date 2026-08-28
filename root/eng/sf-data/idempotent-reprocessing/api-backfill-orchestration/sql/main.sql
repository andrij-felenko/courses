CREATE TABLE backfill_job_checkpoints (
    idempotency_token VARCHAR(64) PRIMARY KEY,
    target_table VARCHAR(128) NOT NULL,
    chunk_partition VARCHAR(32) NOT NULL, -- Наприклад: '2026-08-20'
    window_start TIMESTAMP WITH TIME ZONE NOT NULL,
    window_end TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR(16) NOT NULL, -- 'PENDING', 'VALIDATED', 'COMMITTED', 'FAILED'
    worker_id VARCHAR(64) NOT NULL,
    fence_token BIGINT NOT NULL, -- Монотонно зростаючий лічильник для захисту від зомбі-воркерів
    heartbeat_at TIMESTAMP WITH TIME ZONE NOT NULL,
    lease_expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    rows_inserted BIGINT DEFAULT 0,
    metrics_checksum VARCHAR(64),
    error_payload JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
