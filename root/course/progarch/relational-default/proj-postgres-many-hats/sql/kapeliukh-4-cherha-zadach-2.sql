BEGIN;
  SELECT id, device_id, kind, payload
    FROM commands
   WHERE status = 'ready'
   ORDER BY created_at            -- FIFO: найстаріша готова першою
   FOR UPDATE SKIP LOCKED         -- зайняті рядки ПРОПУСКАЄМО, а не чекаємо
   LIMIT 1;
  -- ...відправити команду пристрою (швидко)...
  UPDATE commands SET status = 'done' WHERE id = :id;
COMMIT;
