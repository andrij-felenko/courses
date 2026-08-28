CREATE TABLE homes (
    id         bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name       text        NOT NULL,
    tz         text        NOT NULL DEFAULT 'Europe/Kyiv',
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE devices (
    id           bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    home_id      bigint NOT NULL REFERENCES homes(id) ON DELETE CASCADE,
    kind         text   NOT NULL CHECK (kind IN ('thermostat','lock','camera','sensor')),
    serial       text   NOT NULL UNIQUE,
    installed_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX ON devices (home_id);   -- під запит «усі пристрої цього дому»
