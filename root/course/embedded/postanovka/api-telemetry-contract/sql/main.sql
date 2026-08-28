-- Таблиця часових рядів телеметрії
CREATE TABLE telemetry_readings (
    measured_at TIMESTAMPTZ NOT NULL,
    node_id INTEGER NOT NULL,
    seq_num BIGINT NOT NULL,
    temperature_c REAL,
    humidity_pct REAL,
    battery_v REAL,
    flags SMALLINT NOT NULL DEFAULT 0,
    rssi_dbm SMALLINT,
    gateway_id VARCHAR(32),
    PRIMARY KEY (node_id, measured_at)
);

-- Перетворення у гіпертаблицю TimescaleDB з інтервалом партиції 7 днів
SELECT create_hypertable('telemetry_readings', 'measured_at', chunk_time_interval => INTERVAL '7 days');

-- Увімкнення політики компресії старих чанків для економії 90% дискового простору
ALTER TABLE telemetry_readings SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'node_id',
    timescaledb.compress_orderby = 'measured_at DESC'
);

SELECT add_compression_policy('telemetry_readings', INTERVAL '30 days');
