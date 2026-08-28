-- Читання: пристрої дому з останнім конфігом — з'єднання за ключем.
SELECT d.device_id, d.kind, d.room, c.firmware, c.settings
FROM   devices d
JOIN   device_config c ON c.device_id = d.device_id
WHERE  d.home_id = 42;

-- Запис: зміна конфігу як одна неподільна транзакція.
BEGIN;
  UPDATE device_config
     SET firmware = '2.4.1'
   WHERE device_id = 'lock-1';
  INSERT INTO device_config_history(device_id, firmware, changed_at)
       VALUES ('lock-1', '2.4.1', now());
COMMIT;
