-- Таблиці модульного моноліту
CREATE TABLE hourly_aggregates (
    id BIGSERIAL PRIMARY KEY,
    home_id VARCHAR(64) NOT NULL,
    total_energy_kwh NUMERIC(10, 3) NOT NULL,
    avg_temperature_c NUMERIC(5, 2) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE outbox_events (
    id BIGSERIAL PRIMARY KEY,
    aggregate_type VARCHAR(64) NOT NULL,
    aggregate_id VARCHAR(64) NOT NULL,
    event_type VARCHAR(64) NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMPTZ NULL
);

CREATE INDEX idx_outbox_unprocessed ON outbox_events (created_at) WHERE processed_at IS NULL;

-- Атомарне збереження агрегату й події сповіщення
BEGIN TRANSACTION;
  INSERT INTO hourly_aggregates (home_id, total_energy_kwh, avg_temperature_c) 
  VALUES ('home-42', 3.650, 21.80);

  INSERT INTO outbox_events (aggregate_type, aggregate_id, event_type, payload) 
  VALUES ('HomeAggregate', 'home-42', 'HIGH_ENERGY_ALERT', '{"home_id": "home-42", "energy_kwh": 3.650}');
COMMIT;
