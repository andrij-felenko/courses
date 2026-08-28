-- Таблиця станів вхідних повідомлень (Transactional Inbox)
CREATE TABLE consumer_inbox (
    message_id VARCHAR(128) NOT NULL,
    consumer_group VARCHAR(64) NOT NULL,
    topic VARCHAR(128) NOT NULL,
    partition_id INTEGER NOT NULL,
    message_offset BIGINT NOT NULL,
    
    -- Стан обробки: PENDING, IN_PROGRESS, COMPLETED, QUARANTINED
    status VARCHAR(24) NOT NULL DEFAULT 'PENDING',
    
    -- Детермінований ключ для зовнішніх викликів (SHA-256)
    outbound_idempotency_key VARCHAR(128) NOT NULL,
    
    -- Зовнішній ідентифікатор транзакції (наприклад, stripe_charge_id)
    external_reference VARCHAR(128),
    
    -- Облік спроб доставки та захист від отруйної петлі
    delivery_attempts INTEGER NOT NULL DEFAULT 1,
    last_error_message TEXT,
    
    -- Оренда обробки (Lease) для запобігання гонкам воркерів
    worker_lease_id UUID,
    lease_expires_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    
    PRIMARY KEY (consumer_group, message_id)
);

-- Індекс для фонового очищення застарілих ключів за вікном TTL
CREATE INDEX idx_consumer_inbox_ttl ON consumer_inbox (created_at)
WHERE status = 'COMPLETED';

-- Індекс для виявлення завислих орендованих повідомлень (Lease Timeout)
CREATE INDEX idx_consumer_inbox_lease ON consumer_inbox (lease_expires_at)
WHERE status = 'IN_PROGRESS';

-- Таблиця огорожі епох для захисту від зомбі-воркерів при ребалансах
CREATE TABLE partition_epoch_fences (
    consumer_group VARCHAR(64) NOT NULL,
    topic VARCHAR(128) NOT NULL,
    partition_id INTEGER NOT NULL,
    current_generation_epoch BIGINT NOT NULL DEFAULT 1,
    active_worker_id VARCHAR(128) NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    PRIMARY KEY (consumer_group, topic, partition_id)
);
