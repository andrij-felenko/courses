CREATE TABLE customers (
    jurisdiction_code VARCHAR(8) NOT NULL, -- 'EU_EEA', 'US_FED', 'APAC'
    tenant_id         UUID NOT NULL,
    user_id           UUID NOT NULL,
    full_name         VARCHAR(128) NOT NULL,
    email             VARCHAR(128) NOT NULL,
    balance           DECIMAL(18, 2) NOT NULL,
    created_at        TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (jurisdiction_code, tenant_id, user_id)
);
