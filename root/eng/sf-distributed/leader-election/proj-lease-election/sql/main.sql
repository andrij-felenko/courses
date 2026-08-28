-- Таблиця стану координації білінгу
-- Стовпець last_fencing_token містить максимальний зареєстрований номер епохи

UPDATE billing_execution_state
SET 
    last_processed_id = 894520,
    last_fencing_token = 42,
    updated_at = NOW()
WHERE 
    service_name = 'payment-aggregator' 
    AND last_fencing_token <= 42;
