CREATE TABLE payments (
  id           BIGINT      PRIMARY KEY,
  kind         VARCHAR(16) NOT NULL,          -- розрізнювач: 'card' | 'bank'
  amount_cents BIGINT      NOT NULL,
  currency     CHAR(3)     NOT NULL,
  created_at   TIMESTAMPTZ NOT NULL,
  -- поля CardPayment (NULL у банківських рядках)
  card_last4   CHAR(4),
  auth_code    VARCHAR(32),
  -- поля BankTransfer (NULL у карткових рядках)
  iban         VARCHAR(34),
  reference    VARCHAR(64),
  CHECK (kind IN ('card', 'bank'))
);
