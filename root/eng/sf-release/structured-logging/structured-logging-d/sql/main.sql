CREATE TABLE telemetry.logs
(
    timestamp DateTime64(6, 'UTC') CODEC(DoubleDelta, ZSTD(1)),
    service_name LowCardinality(String) CODEC(ZSTD(1)),
    environment LowCardinality(String) CODEC(ZSTD(1)),
    severity_number UInt8 CODEC(ZSTD(1)),
    severity_text LowCardinality(String) CODEC(ZSTD(1)),
    body String CODEC(ZSTD(3)),
    trace_id FixedString(32) CODEC(ZSTD(1)),
    span_id FixedString(16) CODEC(ZSTD(1)),
    attributes Map(String, String) CODEC(ZSTD(1)),
    INDEX idx_trace trace_id TYPE bloom_filter(0.01) GRANULARITY 1
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
PRIMARY KEY (service_name, severity_number, timestamp)
ORDER BY (service_name, severity_number, timestamp, trace_id);
