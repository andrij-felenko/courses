-- Таблиця з підтримкою огорожі
CREATE TABLE bank_accounts (
    account_id   BIGINT PRIMARY KEY,
    balance      NUMERIC(18, 2) NOT NULL,
    fencing_token BIGINT NOT NULL DEFAULT 0
);

-- Атомарний запис із валідацією токена
UPDATE bank_accounts
SET balance = 3000.00,
    fencing_token = 35
WHERE account_id = 48291
  AND fencing_token < 35;
