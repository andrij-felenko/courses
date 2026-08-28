CREATE TABLE payments (                        -- спільний корінь
  id           BIGINT      PRIMARY KEY,
  kind         VARCHAR(16) NOT NULL,
  amount_cents BIGINT      NOT NULL,
  currency     CHAR(3)     NOT NULL,
  created_at   TIMESTAMPTZ NOT NULL,
  CHECK (kind IN ('card', 'bank'))
);
CREATE TABLE card_payments (
  id         BIGINT      PRIMARY KEY REFERENCES payments(id) ON DELETE CASCADE,
  card_last4 CHAR(4)     NOT NULL,              -- NOT NULL повернувся!
  auth_code  VARCHAR(32) NOT NULL
);
CREATE TABLE bank_transfers (
  id        BIGINT      PRIMARY KEY REFERENCES payments(id) ON DELETE CASCADE,
  iban      VARCHAR(34) NOT NULL,
  reference VARCHAR(64) NOT NULL
);
