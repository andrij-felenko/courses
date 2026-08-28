-- read-модель: денормалізований зріз ПІД дашборд, одна річ на пристрій
CREATE TABLE dashboard.device_card (
  device_id   uuid PRIMARY KEY,
  home_id     uuid NOT NULL,
  name        text NOT NULL,       -- прийшло з control
  room        text,                -- прийшло з control
  last_value  double precision,    -- прийшло з telemetry
  last_unit   text,
  last_at     timestamptz          -- коли зроблено вимір
);
