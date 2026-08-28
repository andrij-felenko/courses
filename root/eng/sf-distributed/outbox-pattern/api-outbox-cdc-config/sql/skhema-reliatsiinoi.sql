CREATE TABLE public.outbox (
    id             UUID                     NOT NULL,
    aggregate_type VARCHAR(128)             NOT NULL,
    aggregate_id   VARCHAR(128)             NOT NULL,
    type           VARCHAR(256)             NOT NULL,
    payload        JSONB                    NOT NULL,
    headers        JSONB                    DEFAULT '{}'::jsonb NOT NULL,
    created_at     TIMESTAMP WITH TIME ZONE DEFAULT clock_timestamp() NOT NULL,
    
    CONSTRAINT pk_outbox PRIMARY KEY (id)
)
WITH (
    autovacuum_vacuum_scale_factor = 0.01,
    autovacuum_vacuum_threshold = 100,
    autovacuum_vacuum_cost_limit = 2000,
    fillfactor = 90
);

-- Індекс для режиму періодичного опитування (Polling Publisher).
-- Якщо ретрансляція здійснюється виключно через CDC (Debezium), індекс не потрібен.
CREATE INDEX idx_outbox_polling ON public.outbox (created_at ASC)
    INCLUDE (aggregate_id, aggregate_type, type);
