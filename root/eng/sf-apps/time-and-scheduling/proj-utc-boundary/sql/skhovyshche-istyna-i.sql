CREATE TABLE reminder (
    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id     bigint      NOT NULL,
    title       text        NOT NULL,

    -- ІСТИНА: те, що сказала людина
    local_wall  timestamp   NOT NULL,   -- без зони: «2026-10-25 03:30»
    zone        text        NOT NULL,   -- 'Europe/Kyiv' — назва зони, не зсув

    -- ПОХІДНЕ: те, за чим сканує планувальник
    fire_at     timestamptz NOT NULL,
    fired_at    timestamptz,            -- NULL, доки не спрацювало
    created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX reminder_due  ON reminder (fire_at) WHERE fired_at IS NULL;
CREATE INDEX reminder_span ON reminder (user_id, fire_at);
