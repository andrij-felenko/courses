CREATE TABLE telemetry (
    device_id bigint      NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    ts        timestamptz NOT NULL,
    metric    text        NOT NULL,          -- 'temp_c','motion','lock_state'
    value     double precision NOT NULL
) PARTITION BY RANGE (ts);                   -- секціювання за часом (Postgres 10+)

-- місячні секції: свіже окремо, старе — цілим шматком під відкидання
CREATE TABLE telemetry_2026_07 PARTITION OF telemetry
    FOR VALUES FROM ('2026-07-01') TO ('2026-08-01');
CREATE TABLE telemetry_2026_08 PARTITION OF telemetry
    FOR VALUES FROM ('2026-08-01') TO ('2026-09-01');

-- індекс під головний запит «цей пристрій за цей проміжок»;
-- створений на батьківській таблиці, він лягає на кожну секцію
CREATE INDEX ON telemetry (device_id, ts DESC);
