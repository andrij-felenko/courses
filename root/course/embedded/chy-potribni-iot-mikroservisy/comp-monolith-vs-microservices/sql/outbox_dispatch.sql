-- Диспетчер черги вихідних команд: єдине місце, де база віддає роботу мережі.
-- Обидва запити виконує фоновий воркер моноліту; між ними він публікує
-- повідомлення в MQTT-брокер.

-- Крок 1. Забрати пачку невідправлених команд і одразу порахувати спробу.
-- SKIP LOCKED дозволяє тримати кілька воркерів: кожен бере СВОЇ рядки й не
-- чекає на чужі блокування.
WITH batch AS (
    SELECT id
      FROM outbound_commands
     WHERE sent_at IS NULL
       AND attempts < 10
     ORDER BY id
     LIMIT 64
     FOR UPDATE SKIP LOCKED
)
UPDATE outbound_commands c
   SET attempts = c.attempts + 1
  FROM batch b
 WHERE c.id = b.id
RETURNING c.id, c.device_id, c.topic, c.payload;

-- ... воркер публікує кожен рядок у MQTT і чекає PUBACK (QoS 1) ...

-- Крок 2. Позначити підтверджені брокером. Непідтверджені лишаються з
-- sent_at IS NULL і повертаються в наступну пачку; після 10 спроб випадають
-- з вибірки й чекають на людину.
UPDATE outbound_commands
   SET sent_at = now()
 WHERE id = ANY($1::bigint[]);   -- $1 — ідентифікатори, підтверджені брокером
