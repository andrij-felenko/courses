CREATE TABLE task_queue (
    id BIGSERIAL PRIMARY KEY,
    payload TEXT NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'pending',
    attempts INT NOT NULL DEFAULT 0,
    max_attempts INT NOT NULL DEFAULT 3,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Частковий індекс для миттєвого пошуку активних завдань за пріоритетом та ідентифікатором
CREATE INDEX idx_task_queue_pending ON task_queue (status, id) 
WHERE status = 'pending';
