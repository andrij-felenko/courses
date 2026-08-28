CREATE TABLE node_telemetry (
    time TIMESTAMPTZ NOT NULL,
    node_id INT NOT NULL REFERENCES devices(id),
    temperature REAL,
    humidity REAL,
    vbat_mv SMALLINT,
    fault_flag BOOLEAN DEFAULT FALSE
);
SELECT create_hypertable('node_telemetry', 'time', chunk_time_interval => INTERVAL '1 day');

-- Політика автоматичного стиснення для чанків, старших за 7 днів
ALTER TABLE node_telemetry SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'node_id',
    timescaledb.compress_orderby = 'time DESC'
);
SELECT add_compression_policy('node_telemetry', INTERVAL '7 days');
