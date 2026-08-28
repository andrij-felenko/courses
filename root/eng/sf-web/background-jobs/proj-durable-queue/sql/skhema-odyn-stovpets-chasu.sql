CREATE TABLE jobs (
    id            bigserial   PRIMARY KEY,
    kind          text        NOT NULL,                 -- який обробник виконує
    payload       jsonb       NOT NULL,                 -- аргументи задачі
    status        text        NOT NULL DEFAULT 'ready'
                  CHECK (status IN ('ready', 'dead')),  -- станів лише два
    run_at        timestamptz NOT NULL DEFAULT now(),   -- «не раніше цього моменту»
    attempts      int         NOT NULL DEFAULT 0,       -- скільки разів задачу БРАЛИ
    max_attempts  int         NOT NULL DEFAULT 5,
    locked_by     text,                                 -- хто взяв востаннє
    last_error    text,
    created_at    timestamptz NOT NULL DEFAULT now()
);

-- єдиний індекс, яким ходить застовплення
CREATE INDEX jobs_ready ON jobs (run_at, id) WHERE status = 'ready';
