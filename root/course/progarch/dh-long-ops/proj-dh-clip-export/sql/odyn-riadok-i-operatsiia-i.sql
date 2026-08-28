CREATE TABLE operations (
  id               text PRIMARY KEY,            -- op-42 у /operations/{id}
  idempotency_key  text UNIQUE NOT NULL,        -- ← один намір = один рядок (гонку розсудить індекс)
  status           text NOT NULL DEFAULT 'queued'
                   CHECK (status IN ('queued','running','succeeded','failed','canceled')),
  request          jsonb NOT NULL,              -- {cameraId, from, to} — що саме просили
  progress         int  NOT NULL DEFAULT 0,     -- 0..100, поки running
  result           jsonb,                       -- {url, expiresAt} — коли succeeded
  error            jsonb,                       -- {code, message} — коли failed
  cancel_requested boolean NOT NULL DEFAULT false,
  -- поля черги (той самий рядок працює й задачею):
  lease_id         text,                        -- жетон поточної оренди — НОВИЙ на кожен забір
  lease_expires_at timestamptz,                 -- доки триває оренда цього робітника
  attempt          int  NOT NULL DEFAULT 0,     -- скільки разів задачу забирали
  user_id          text NOT NULL,               -- кому слати пуш наприкінці
  created_at       timestamptz NOT NULL DEFAULT now(),
  expires_at       timestamptz NOT NULL         -- коли прибрати сам запис операції
);

-- індекс для забору: цікаві лише ті, що чекають або чия оренда згасла
CREATE INDEX ops_claimable ON operations (created_at)
  WHERE status IN ('queued','running');
