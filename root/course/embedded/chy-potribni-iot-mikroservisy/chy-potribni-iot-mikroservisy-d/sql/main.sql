BEGIN;
  -- Атомарне оновлення бажаного стану
  UPDATE device_shadow SET desired_temp = 22.5 WHERE device_id = 'ctrl_441';
  
  -- Запис у журнал аудиту
  INSERT INTO audit_log (device_id, event_type, created_at) 
  VALUES ('ctrl_441', 'CONFIG_CHANGE', NOW());
  
  -- Запис у внутрішню чергу відправки (Transactional Outbox)
  INSERT INTO outbound_queue (device_id, topic, payload)
  VALUES ('ctrl_441', 'devices/ctrl_441/set', '{"temp": 22.5}');
COMMIT;
