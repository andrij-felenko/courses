CREATE TABLE IF NOT EXISTS cluster_resources (
    resource_id           VARCHAR(128) PRIMARY KEY,
    payload_data          JSONB NOT NULL,
    highest_fencing_token BIGINT NOT NULL DEFAULT 0,
    last_idempotency_key  VARCHAR(64),
    updated_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_positive_fencing_token CHECK (highest_fencing_token >= 0)
);

CREATE INDEX idx_cluster_resources_fencing ON cluster_resources (resource_id, highest_fencing_token);
