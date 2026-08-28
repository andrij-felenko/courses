-- 1. Таблиця поточного стану пристроїв (Device State / Twin)
CREATE TABLE device_state (
    device_id       VARCHAR(64) PRIMARY KEY,
    last_seen       TIMESTAMPTZ NOT NULL,
    temperature     REAL,
    humidity        REAL,
    relay_state     BOOLEAN,
    battery_voltage REAL,
    rssi            SMALLINT,
    fw_version      VARCHAR(32),
    ip_address      INET,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Індекс для миттєвого виявлення офлайн-пристроїв
CREATE INDEX idx_device_state_last_seen ON device_state (last_seen);

-- 2. Сира таблиця телеметрії (Time-Series Log)
CREATE TABLE telemetry_raw (
    time            TIMESTAMPTZ NOT NULL,
    device_id       VARCHAR(64) NOT NULL,
    temperature     REAL,
    humidity        REAL,
    relay_state     BOOLEAN,
    battery_voltage REAL,
    rssi            SMALLINT
);

-- Перетворення на гіпертаблицю з розміром чанка 1 доба
SELECT create_hypertable('telemetry_raw', 'time', 
                         chunk_time_interval => INTERVAL '1 day');

-- Складений індекс для швидких діапазонних вибірок конкретного пристрою
CREATE INDEX idx_telemetry_device_time ON telemetry_raw (device_id, time DESC);

-- Додатковий BRIN-індекс для надшвидкого глобального сканування часових вікон
CREATE INDEX idx_telemetry_brin_time ON telemetry_raw USING BRIN (time);

-- 3. Безперервний матеріалізований агрегат (Continuous Aggregate 1h)
CREATE MATERIALIZED VIEW telemetry_hourly
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 hour', time) AS bucket,
    device_id,
    COUNT(*)                    AS samples_count,
    AVG(temperature)            AS temp_avg,
    MIN(temperature)            AS temp_min,
    MAX(temperature)            AS temp_max,
    AVG(humidity)               AS humidity_avg,
    AVG(battery_voltage)        AS voltage_avg
FROM telemetry_raw
GROUP BY bucket, device_id
WITH NO DATA;

-- Політика автоматичного оновлення агрегату щогодини
SELECT add_continuous_aggregate_policy('telemetry_hourly',
    start_offset => INTERVAL '3 days',
    end_offset   => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour');

-- Політика утримання: видаляти сирі чанки старші 14 днів
SELECT add_retention_policy('telemetry_raw', INTERVAL '14 days');
