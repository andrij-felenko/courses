-- inbox: журнал уже прийнятих подій. PRIMARY KEY робить дедуп атомарним.
CREATE TABLE inbox (
  event_id    text PRIMARY KEY,
  received_at timestamptz NOT NULL DEFAULT now()
);

-- jobs: черга. Робітник бере рядок під FOR UPDATE SKIP LOCKED.
CREATE TABLE jobs (
  id        bigserial   PRIMARY KEY,
  event_id  text        NOT NULL,
  payload   jsonb       NOT NULL,
  attempts  int         NOT NULL DEFAULT 0,
  run_after timestamptz NOT NULL DEFAULT now()   -- коли задача знову «дозріє» після невдачі
);
CREATE INDEX jobs_ready ON jobs (run_after, id);

-- twin: остання відома правда про пристрій. seq — версія від джерела (проти переупорядкування).
CREATE TABLE twin (
  device_id  text        PRIMARY KEY,
  state      text        NOT NULL,
  seq        bigint      NOT NULL,
  updated_at timestamptz NOT NULL DEFAULT now()
);

-- dead_letter: подія, що не піддалась після N спроб. Лежить тут для очей людини.
CREATE TABLE dead_letter (
  id        bigserial   PRIMARY KEY,
  event_id  text        NOT NULL,
  payload   jsonb       NOT NULL,
  error     text        NOT NULL,
  failed_at timestamptz NOT NULL DEFAULT now()
);
