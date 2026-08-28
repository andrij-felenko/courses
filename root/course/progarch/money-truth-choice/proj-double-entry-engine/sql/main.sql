-- Рахунки (Accounts): первинний довідник
CREATE TABLE accounts (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    code VARCHAR(64) NOT NULL UNIQUE,  -- напр. 'assets:bank:stripe', 'liabilities:user:42'
    type VARCHAR(32) NOT NULL,         -- 'asset', 'liability', 'equity', 'revenue', 'expense'
    currency VARCHAR(3) NOT NULL,      -- ISO-4217, напр. 'USD'
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Ключі ідемпотентності: захист від повторних мережевих запитів
CREATE TABLE idempotency_keys (
    key VARCHAR(128) PRIMARY KEY,
    transaction_id BIGINT,
    status VARCHAR(16) NOT NULL CHECK (status IN ('PROCESSING', 'COMPLETED', 'FAILED')),
    request_hash VARCHAR(64) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Фінансові транзакції (атомарна група проводжень)
CREATE TABLE transactions (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    idempotency_key VARCHAR(128) REFERENCES idempotency_keys(key),
    description TEXT NOT NULL,
    posted_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Проводження (Entries): сирий незмінний лог (Debits / Credits)
CREATE TABLE ledger_entries (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    transaction_id BIGINT NOT NULL REFERENCES transactions(id) ON DELETE RESTRICT,
    account_id BIGINT NOT NULL REFERENCES accounts(id) ON DELETE RESTRICT,
    direction VARCHAR(6) NOT NULL CHECK (direction IN ('DEBIT', 'CREDIT')),
    amount_cents BIGINT NOT NULL CHECK (amount_cents > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_entries_account ON ledger_entries(account_id, id);
