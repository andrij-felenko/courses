UPDATE notification_attempts AS na
SET 
    status = v.status::delivery_status_enum,
    updated_at = NOW()
FROM (VALUES 
    ('550e8400-e29b-41d4-a716-446655440001'::uuid, 'DELIVERED'),
    ('550e8400-e29b-41d4-a716-446655440002'::uuid, 'FAILED_PERMANENT')
) AS v(attempt_id, status)
WHERE na.id = v.attempt_id
  AND status_rank(v.status::delivery_status_enum) > status_rank(na.status);
