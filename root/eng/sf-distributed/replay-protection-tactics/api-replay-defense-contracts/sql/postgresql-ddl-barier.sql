CREATE TABLE distributed_fencing_leases (
    resource_id       VARCHAR(128) PRIMARY KEY,
    owner_node_id     VARCHAR(64)  NOT NULL,
    max_fencing_token BIGINT       NOT NULL,
    lease_expires_at  TIMESTAMPTZ  NOT NULL,
    updated_at        TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- Атомарна перевірка та фіксація токена огорожі
CREATE OR REPLACE FUNCTION verify_and_update_fencing(
    p_resource_id   VARCHAR(128),
    p_node_id       VARCHAR(64),
    p_fencing_token BIGINT,
    p_lease_ttl_ms  INT
) RETURNS BOOLEAN AS $$
DECLARE
    v_current_token BIGINT;
BEGIN
    SELECT max_fencing_token INTO v_current_token
    FROM distributed_fencing_leases
    WHERE resource_id = p_resource_id
    FOR UPDATE;

    IF NOT FOUND THEN
        INSERT INTO distributed_fencing_leases(resource_id, owner_node_id, max_fencing_token, lease_expires_at)
        VALUES (p_resource_id, p_node_id, p_fencing_token, NOW() + (p_lease_ttl_ms || ' milliseconds')::INTERVAL);
        RETURN TRUE;
    END IF;

    IF p_fencing_token > v_current_token THEN
        UPDATE distributed_fencing_leases
        SET owner_node_id = p_node_id,
            max_fencing_token = p_fencing_token,
            lease_expires_at = NOW() + (p_lease_ttl_ms || ' milliseconds')::INTERVAL,
            updated_at = NOW()
        WHERE resource_id = p_resource_id;
        RETURN TRUE;
    ELSE
        -- Запізнілий запит зомбі-воркера відхиляється
        RETURN FALSE;
    END IF;
END;
$$ LANGUAGE plpgsql;
