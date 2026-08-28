CREATE TABLE commands (
    id         bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    device_id  bigint NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
    kind       text   NOT NULL,                 -- 'lock','unlock','set_temp'…
    payload    jsonb  NOT NULL DEFAULT '{}',
    status     text   NOT NULL DEFAULT 'ready'
                      CHECK (status IN ('ready','done','failed')),
    created_at timestamptz NOT NULL DEFAULT now()
);

-- ЧАСТКОВИЙ індекс: тільки готові рядки, тож скан лишається дешевим,
-- скільки б «done» не накопичилось у хвості
CREATE INDEX commands_ready ON commands (created_at) WHERE status = 'ready';
