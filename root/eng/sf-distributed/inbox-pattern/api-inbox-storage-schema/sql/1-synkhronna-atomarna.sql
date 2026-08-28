-- Виконується в межах єдиної транзакції разом із бізнес-змінами
INSERT INTO inbox_messages (
    message_id, 
    consumer_group, 
    event_type, 
    payload, 
    status, 
    processed_at
) VALUES (
    :message_id, 
    :consumer_group, 
    :event_type, 
    :payload, 
    'PROCESSED', 
    NOW()
) ON CONFLICT (message_id, consumer_group) DO NOTHING;

-- Перевірка кількості вставлених рядків:
-- Якщо rows_affected == 0 -> дублікат! Відкочуємо транзакцію і негайно шлемо ACK брокеру.
-- Якщо rows_affected == 1 -> нове повідомлення. Продовжуємо виконання доменного коду.
