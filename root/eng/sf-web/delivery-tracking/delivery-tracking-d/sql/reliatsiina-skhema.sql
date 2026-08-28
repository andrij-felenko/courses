CREATE TYPE delivery_status_enum AS ENUM (
  'CREATED', 'DISPATCHED', 'SENT',
  'DELIVERED', 'OPENED', 'CLICKED',
  'FAILED_TRANSIENT', 'FAILED_PERMANENT', 'EXPIRED'
);

-- Таблиця агрегатів повідомлень (секціонована за часом створення)
CREATE TABLE notifications (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL,
  cascade_route TEXT[] NOT NULL,
  current_status delivery_status_enum NOT NULL DEFAULT 'CREATED',
  expires_at TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
) PARTITION BY RANGE (created_at);

-- Таблиця окремих спроб відправки через кожен канал
CREATE TABLE notification_attempts (
  id UUID PRIMARY KEY,
  notification_id UUID NOT NULL,
  channel TEXT NOT NULL,
  provider TEXT NOT NULL,
  provider_msg_id TEXT,
  status delivery_status_enum NOT NULL,
  error_code TEXT,
  dispatched_at TIMESTAMPTZ NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL
);

-- Буферний журнал сирих вебхуків для швидкого прийому телеметрії
CREATE TABLE delivery_events (
  event_id TEXT PRIMARY KEY,
  notification_id UUID NOT NULL,
  status delivery_status_enum NOT NULL,
  raw_payload JSONB NOT NULL,
  received_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
