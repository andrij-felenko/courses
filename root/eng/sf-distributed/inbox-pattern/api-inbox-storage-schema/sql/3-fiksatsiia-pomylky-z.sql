UPDATE inbox_messages
SET retry_count = retry_count + 1,
    last_error = :error_message,
    status = CASE 
        WHEN retry_count + 1 >= max_retries THEN 'FAILED' 
        ELSE 'RECEIVED' 
    END,
    -- Якщо статус лишається RECEIVED, відсуваємо час наступної обробки (Backoff)
    locked_until = CASE 
        WHEN retry_count + 1 < max_retries THEN NOW() + (POWER(2, retry_count) || ' seconds')::INTERVAL
        ELSE NULL 
    END,
    locked_by = NULL
WHERE message_id = :message_id
  AND consumer_group = :consumer_group;
