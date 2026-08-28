DELETE FROM mysql_query_rules;

-- Правило 1: Усі транзакції з блокуванням рядків відправляти на Primary (hostgroup 0)
INSERT INTO mysql_query_rules (
    rule_id, active, match_pattern, destination_hostgroup, apply
) VALUES (
    10, 1, '^SELECT.*FOR (UPDATE|SHARE)', 0, 1
);

-- Правило 2: Запити читання відправляти на пул реплік (hostgroup 1)
INSERT INTO mysql_query_rules (
    rule_id, active, match_pattern, destination_hostgroup, apply
) VALUES (
    20, 1, '^SELECT', 1, 1
);

-- Правило 3: Усі інші запити (INSERT, UPDATE, DELETE, DDL, SET) відправляти на Primary (hostgroup 0)
INSERT INTO mysql_query_rules (
    rule_id, active, match_pattern, destination_hostgroup, apply
) VALUES (
    30, 1, '.*', 0, 1
);

LOAD MYSQL QUERY RULES TO RUNTIME;
SAVE MYSQL QUERY RULES TO DISK;
