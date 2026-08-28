CREATE TABLE webhook_inbox (
    event_id     TEXT        PRIMARY KEY,        -- ідентифікатор ПРОВАЙДЕРА, не наш
    type         TEXT        NOT NULL,           -- payment.succeeded, push, …
    payload      JSONB       NOT NULL,           -- сире тіло, збережене як прийшло
    status       TEXT        NOT NULL DEFAULT 'received',  -- received→processing→done | dead
    attempts     INT         NOT NULL DEFAULT 0,
    received_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    processed_at TIMESTAMPTZ
);

-- Курсор звірки: доки ми дочитали чужий журнал подій.
CREATE TABLE reconciliation_cursor (
    source    TEXT        PRIMARY KEY,
    last_seen TIMESTAMPTZ NOT NULL
);
