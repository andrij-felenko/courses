CREATE TABLE events (
    id        bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    home_id   bigint NOT NULL REFERENCES homes(id) ON DELETE CASCADE,
    device_id bigint REFERENCES devices(id) ON DELETE SET NULL,
    at        timestamptz NOT NULL DEFAULT now(),
    message   text NOT NULL,
    -- база сама рахує tsvector при вставці/оновленні (Postgres 12+)
    tsv tsvector GENERATED ALWAYS AS (to_tsvector('simple', message)) STORED
);

CREATE INDEX events_tsv_gin ON events USING gin (tsv);
