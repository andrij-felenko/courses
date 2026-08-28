CREATE TABLE clips (
  id         BIGSERIAL PRIMARY KEY,
  home_id    BIGINT      NOT NULL,
  url        TEXT        NOT NULL,          -- сирий файл у сховищі
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE jobs (
  id         BIGSERIAL PRIMARY KEY,
  type       TEXT        NOT NULL,
  payload    JSONB       NOT NULL,
  status     TEXT        NOT NULL DEFAULT 'ready',   -- ready | running | done
  locked_by  TEXT,                                   -- який воркер узяв
  locked_at  TIMESTAMPTZ,                            -- коли взяв (для оренди)
  attempts   INT         NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX jobs_ready_idx ON jobs (id) WHERE status = 'ready';

CREATE TABLE renditions (              -- РЕЗУЛЬТАТ перекодування
  clip_id BIGINT NOT NULL,
  profile TEXT   NOT NULL,             -- напр. 'h264-720p'
  path    TEXT   NOT NULL,
  PRIMARY KEY (clip_id, profile)       -- один вихід на (кліп, профіль) — ключ ідемпотентності
);

CREATE TABLE outbox (
  id           BIGSERIAL PRIMARY KEY,
  topic        TEXT        NOT NULL,
  payload      JSONB       NOT NULL,
  delivered_at TIMESTAMPTZ,            -- NULL, поки relay не доправив у брокер
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
