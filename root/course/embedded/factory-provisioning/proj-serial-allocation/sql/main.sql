-- Один рядок на серійний номер. Стан рухається free → reserved → used.
CREATE TABLE serials (
    serial      INTEGER PRIMARY KEY,   -- саме число (формат назви — окремо)
    state       TEXT NOT NULL          -- 'free' | 'reserved' | 'used'
                CHECK (state IN ('free','reserved','used')),
    station     TEXT,                  -- яка станція тримає резерв (для відкату)
    reserved_at INTEGER,               -- коли зарезервовано (unix-час, для відкату)
    used_at     INTEGER                -- коли підтверджено (для відстежуваності)
);

-- Прискорити пошук наступного вільного й пошук завислих резервів.
CREATE INDEX idx_serials_state ON serials(state);
