CREATE TABLE outbound_idempotency_log (
    id BIGSERIAL PRIMARY KEY,
    idempotency_key VARCHAR(255) NOT NULL UNIQUE,
    payload_hash VARCHAR(64) NOT NULL,
    target_url VARCHAR(1024) NOT NULL,
    http_method VARCHAR(10) NOT NULL DEFAULT 'POST',
    request_headers JSONB NOT NULL,
    request_body JSONB NOT NULL,
    
    state VARCHAR(32) NOT NULL DEFAULT 'PENDING', -- PENDING, IN_FLIGHT, COMPLETED, FAILED_FATAL
    response_status INT NULL,
    response_headers JSONB NULL,
    response_body TEXT NULL,
    
    retry_count INT NOT NULL DEFAULT 0,
    max_retries INT NOT NULL DEFAULT 5,
    next_retry_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_outbound_pending ON outbound_idempotency_log (state, next_retry_at) 
WHERE state IN ('PENDING', 'IN_FLIGHT');
