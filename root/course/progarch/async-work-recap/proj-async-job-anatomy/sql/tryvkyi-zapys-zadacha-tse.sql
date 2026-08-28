CREATE TABLE job (
  id            BIGSERIAL PRIMARY KEY,
  key           TEXT NOT NULL UNIQUE,             -- ключ ідемпотентності: 'hub-8f3:2.4.1'
  payload       JSONB NOT NULL,                   -- що робити: {hub, version}
  batch_id      TEXT,                             -- до якого розкочування належить
  state         TEXT NOT NULL DEFAULT 'queued',   -- queued | running | done | dead
  attempts      INT  NOT NULL DEFAULT 0,          -- скільки разів уже брали в роботу
  max_attempts  INT  NOT NULL DEFAULT 10,         -- після скількох здаємося
  run_after     TIMESTAMPTZ NOT NULL DEFAULT now(), -- не чіпати раніше цього часу
  locked_until  TIMESTAMPTZ,                      -- visibility-timeout: доти клеймо дійсне
  last_error    TEXT,                             -- чим упала остання спроба
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- швидко знаходити готові до забору рядки, не читаючи всю таблицю
CREATE INDEX job_pick_idx ON job (state, run_after);
