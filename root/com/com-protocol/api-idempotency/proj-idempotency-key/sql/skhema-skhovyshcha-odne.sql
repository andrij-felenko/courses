CREATE TABLE idempotency_keys (
    user_id          text        NOT NULL,   -- власник ключа
    request_path     text        NOT NULL,   -- ендпоінт, до якого ключ прив'язаний
    key              text        NOT NULL,   -- сам Idempotency-Key від клієнта
    request_hash     bytea       NOT NULL,   -- відбиток тіла запиту (SHA-256)
    state            text        NOT NULL    -- автомат: лише два стани
                     CHECK (state IN ('in_progress', 'completed')),
    response_status  int,                     -- заповнюється при 'completed'
    response_headers jsonb,                   -- відібрані заголовки для відтворення
    response_body    bytea,                   -- ТОЧНІ байти відповіді
    locked_at        timestamptz NOT NULL DEFAULT now(),  -- коли взято claim (оренда)
    completed_at     timestamptz,
    expires_at       timestamptz NOT NULL,    -- доки ключ живий (вікно повторів клієнта)
    PRIMARY KEY (user_id, request_path, key)
);

CREATE INDEX idempotency_keys_expiry ON idempotency_keys (expires_at);
