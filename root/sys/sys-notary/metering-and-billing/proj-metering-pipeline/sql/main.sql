-- 1. Сирий журнал подій споживання з дедуплікацією
CREATE TABLE usage_events (
    event_id          TEXT PRIMARY KEY,          -- UUID або зовнішній ідентифікатор події
    idempotency_key   TEXT NOT NULL UNIQUE,      -- SHA-256 відбиток (tenant_id + request_id + source)
    tenant_id         TEXT NOT NULL,
    metric_name       TEXT NOT NULL,             -- 'api_requests', 'llm_tokens', 'egress_bytes'
    quantity          BIGINT NOT NULL,           -- обсяг споживання (ціле число)
    occurred_at       TIMESTAMPTZ NOT NULL,      -- точний час події на клієнті/воркері
    ingested_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    properties        JSONB                      -- метадані (регіон, модель, тип операції)
);

CREATE INDEX idx_usage_events_tenant_window 
ON usage_events (tenant_id, metric_name, occurred_at);

-- 2. Активні резервації кредитів (Hold Pattern)
CREATE TABLE credit_reservations (
    reservation_id    TEXT PRIMARY KEY,
    tenant_id         TEXT NOT NULL,
    reserved_micros   BIGINT NOT NULL,           -- заблокована сума в мікродоларах ($1 = 1 000 000)
    state             TEXT NOT NULL CHECK (state IN ('active', 'settled', 'released')),
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at        TIMESTAMPTZ NOT NULL       -- тайм-аут автоскасування завислого холду
);

-- 3. Незмінний журнал подвійного запису (Ledger)
CREATE TABLE ledger_entries (
    entry_id          BIGSERIAL PRIMARY KEY,
    transaction_id    TEXT NOT NULL,             -- логічне групування двох проводок (дебет і кредит)
    account_id        TEXT NOT NULL,             -- 'liability:customer_123', 'revenue:api_usage'
    account_type      TEXT NOT NULL CHECK (account_type IN ('asset', 'liability', 'revenue', 'expense')),
    amount_micros     BIGINT NOT NULL,           -- додатне для збільшення, від'ємне для зменшення
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    reference_id      TEXT                       -- зв'язок з event_id, reservation_id чи інвойсом
);

CREATE INDEX idx_ledger_account ON ledger_entries (account_id, created_at);
