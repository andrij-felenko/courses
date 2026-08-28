CREATE TABLE card_payments (
  id           BIGINT      PRIMARY KEY,
  amount_cents BIGINT      NOT NULL,           -- спільні колонки —
  currency     CHAR(3)     NOT NULL,           --   дубльовані в обох
  created_at   TIMESTAMPTZ NOT NULL,           --   таблицях
  card_last4   CHAR(4)     NOT NULL,
  auth_code    VARCHAR(32) NOT NULL
);
CREATE TABLE bank_transfers (
  id           BIGINT      PRIMARY KEY,
  amount_cents BIGINT      NOT NULL,
  currency     CHAR(3)     NOT NULL,
  created_at   TIMESTAMPTZ NOT NULL,
  iban         VARCHAR(34) NOT NULL,
  reference    VARCHAR(64) NOT NULL
);
