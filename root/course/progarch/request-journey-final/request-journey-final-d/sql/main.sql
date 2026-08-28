BEGIN TRANSACTION;

-- 1. Оновлення бажаного стану двійника пристрою
UPDATE device_twins 
SET desired_state = '{"lock_state":"UNLOCKED"}',
    version = version + 1,
    updated_at = NOW()
WHERE device_id = 'lock_front_door' AND home_id = 'hm_77a112233';

-- 2. Запис події у транзакційний Outbox
INSERT INTO outbox_messages (
    aggregate_type, aggregate_id, event_type, payload, trace_id, span_id, created_at
) VALUES (
    'DeviceTwin', 
    'lock_front_door', 
    'LockUnlockCommanded', 
    '{"action":"UNLOCKED","user_id":"usr_99a8b7c6d5","home_id":"hm_77a112233"}', 
    '4bf92f3577b34da6a3ce929d0e0e4736', 
    '00f067aa0ba902b7', 
    NOW()
);

COMMIT;
