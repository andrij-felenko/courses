CREATE TABLE aggregation_items (
    correlation_id VARCHAR(64) NOT NULL,
    sequence_number BIGINT NOT NULL,
    payload JSONB NOT NULL,
    received_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (correlation_id, sequence_number)
);

CREATE TABLE aggregation_sessions (
    correlation_id VARCHAR(64) PRIMARY KEY,
    expected_total BIGINT,
    items_count BIGINT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'COLLECTING'
);
