UPDATE notification_attempts
SET 
    status = :new_status,
    updated_at = NOW()
WHERE id = :attempt_id
  AND (
      -- Дозволяємо перехід уперед за прогресивною шкалою успіху
      status_rank(:new_status) > status_rank(status)
      -- Дозволяємо перехід у термінальну помилку лише до моменту фізичної доставки
      OR (:new_status IN ('FAILED_PERMANENT', 'EXPIRED') AND status_rank(status) < status_rank('DELIVERED'))
  );
