-- Статус учасників групи та їхні ролі
SELECT 
    member_id, 
    member_host, 
    member_port, 
    member_state, 
    member_role, 
    member_version 
FROM performance_schema.replication_group_members;

-- Моніторинг черги сертифікації та кількості відхилених транзакцій
SELECT 
    channel_name,
    count_transactions_in_queue AS cert_queue_len,
    count_transactions_checked AS total_checked,
    count_conflicts_detected AS total_conflicts,
    count_transactions_rows_validating AS cert_db_size
FROM performance_schema.replication_group_member_stats;
