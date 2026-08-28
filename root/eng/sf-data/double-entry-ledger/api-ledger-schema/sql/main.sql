-- 1. Перелік класів рахунків згідно з фундаментальною бухгалтерською моделлю
CREATE TYPE account_type AS ENUM (
    'ASSET',      -- Активи (кошти в банку, каса, дебіторська заборгованість)
    'LIABILITY',  -- Зобов'язання (кошти клієнтів, борги перед постачальниками)
    'EQUITY',     -- Власний капітал (статутний фонд, нерозподілений прибуток)
    'REVENUE',    -- Доходи (комісії, плата за послуги, виручка)
    'EXPENSE'     -- Витрати (оренда, комісії еквайрингу, серверна інфраструктура)
);

-- 2. Таблиця рахунків (Chart of Accounts)
CREATE TABLE accounts (
    id            BIGSERIAL PRIMARY KEY,
    code          VARCHAR(64) NOT NULL UNIQUE,
    name          VARCHAR(255) NOT NULL,
    type          account_type NOT NULL,
    currency      CHAR(3) NOT NULL DEFAULT 'UAH',
    is_active     BOOLEAN NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3. Заголовки транзакцій (Transaction Headers)
CREATE TABLE transactions (
    id              BIGSERIAL PRIMARY KEY,
    idempotency_key VARCHAR(128) NOT NULL UNIQUE,
    description     TEXT NOT NULL,
    posted_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 4. Незмінний журнал проводок (Postings Log)
CREATE TABLE postings (
    id             BIGSERIAL PRIMARY KEY,
    transaction_id BIGINT NOT NULL REFERENCES transactions(id) ON DELETE RESTRICT,
    account_id     BIGINT NOT NULL REFERENCES accounts(id) ON DELETE RESTRICT,
    amount         BIGINT NOT NULL, -- Додатне значення: дебет/зарахування, від'ємне: кредит/списання
    sequence_num   BIGSERIAL NOT NULL UNIQUE,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_posting_amount_non_zero CHECK (amount <> 0)
);

-- Індекси для оптимізації читання та звірок
CREATE INDEX idx_postings_account_seq ON postings(account_id, sequence_num);
CREATE INDEX idx_postings_tx_id ON postings(transaction_id);

-- 5. Тригер захисту незмінності журналу (Immutability Enforcement)
CREATE OR REPLACE FUNCTION prevent_posting_mutation()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Порушення аудиту: незмінний журнал проводок (postings) заборонено модифікувати або видаляти. Виправлення дозволено лише через сторнування.';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_protect_postings
BEFORE UPDATE OR DELETE ON postings
FOR EACH ROW EXECUTE FUNCTION prevent_posting_mutation();

-- 6. Відкладений перевірочний тригер інваріанта нульової суми транзакції
CREATE OR REPLACE FUNCTION check_transaction_zero_sum()
RETURNS TRIGGER AS $$
DECLARE
    v_sum BIGINT;
    v_count INT;
BEGIN
    SELECT COALESCE(SUM(amount), 0), COUNT(*)
    INTO v_sum, v_count
    FROM postings
    WHERE transaction_id = NEW.transaction_id;

    IF v_count < 2 THEN
        RAISE EXCEPTION 'Транзакція #% недійсні: проведення повинно містити щонайменше дві проводки (знайдено %)',
            NEW.transaction_id, v_count;
    END IF;

    IF v_sum <> 0 THEN
        RAISE EXCEPTION 'Порушення балансу: сума проводок транзакції #% становить % замість очікуваного 0',
            NEW.transaction_id, v_sum;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE CONSTRAINT TRIGGER trg_enforce_zero_sum
AFTER INSERT ON postings
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW EXECUTE FUNCTION check_transaction_zero_sum();

-- 7. Таблиця періодичних матеріалізованих знімків залишків (Balance Snapshots)
CREATE TABLE balance_snapshots (
    account_id     BIGINT NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    sequence_num   BIGINT NOT NULL,
    balance        BIGINT NOT NULL,
    snapshot_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (account_id, sequence_num)
);
