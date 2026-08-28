CREATE TABLE crypto_key_catalog (
    key_id              UUID PRIMARY KEY,
    tenant_id           UUID NOT NULL,
    entity_type         VARCHAR(64) NOT NULL,
    entity_id           VARCHAR(128) NOT NULL,
    kek_identifier      VARCHAR(256) NOT NULL,
    encrypted_dek       BYTEA NOT NULL,
    dek_algorithm       VARCHAR(32) NOT NULL DEFAULT 'AES-256-GCM',
    key_status          VARCHAR(16) NOT NULL DEFAULT 'ACTIVE',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_rotated_at     TIMESTAMPTZ,
    shredded_at         TIMESTAMPTZ,
    audit_digest_sha256 BYTEA,
    
    CONSTRAINT chk_key_status CHECK (key_status IN ('ACTIVE', 'REVOKED', 'SHREDDED')),
    CONSTRAINT uq_entity_key UNIQUE (tenant_id, entity_type, entity_id)
);

CREATE INDEX idx_key_catalog_status ON crypto_key_catalog (key_status) WHERE key_status = 'ACTIVE';
