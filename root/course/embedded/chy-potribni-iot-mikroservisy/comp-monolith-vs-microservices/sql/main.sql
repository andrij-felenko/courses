BEGIN;
  -- 1. Перевірка і блокування запису
  SELECT state, firmware_ver FROM devices WHERE id = 'node_1042' FOR UPDATE;
  
  -- 2. Оновлення конфігурації
  UPDATE device_configs SET max_current = 32.0, mode = 'auto' WHERE device_id = 'node_1042';
  
  -- 3. Запис у журнал аудиту
  INSERT INTO audit_logs (device_id, action, timestamp) VALUES ('node_1042', 'SET_LIMIT_32A', NOW());
  
  -- 4. Запис у локальну таблицю вихідних команд (Transactional Outbox)
  INSERT INTO outbound_commands (device_id, payload) VALUES ('node_1042', '{"cmd":"set_limit","val":32}');
COMMIT;
