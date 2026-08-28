-- 1. Створення службового користувача з правами реплікації
CREATE USER cdc_debezium_user WITH REPLICATION ENCRYPTED PASSWORD 'strong_password';

-- 2. Надання прав на читання схеми та таблиці outbox
GRANT USAGE ON SCHEMA public TO cdc_debezium_user;
GRANT SELECT ON TABLE public.outbox TO cdc_debezium_user;

-- 3. Створення таблиці для механізму пульсу (heartbeat)
CREATE TABLE public.outbox_heartbeat (
    id             INT PRIMARY KEY,
    last_heartbeat TIMESTAMPTZ NOT NULL
);
INSERT INTO public.outbox_heartbeat (id, last_heartbeat) VALUES (1, NOW());
GRANT SELECT, UPDATE ON TABLE public.outbox_heartbeat TO cdc_debezium_user;

-- 4. Створення вибіркової публікації тільки для таблиці outbox
CREATE PUBLICATION dbz_outbox_publication FOR TABLE public.outbox, public.outbox_heartbeat;
