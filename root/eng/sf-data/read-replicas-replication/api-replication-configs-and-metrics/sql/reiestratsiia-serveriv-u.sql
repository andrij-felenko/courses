-- Очистити таблицю серверів
DELETE FROM mysql_servers;

-- Реєстрація первинного вузла у групі запису (hostgroup 0)
INSERT INTO mysql_servers (
    hostgroup_id, hostname, port, weight, max_connections, max_replication_lag
) VALUES (
    0, '10.0.1.10', 3306, 1000, 1000, 0
);

-- Реєстрація пулу реплік у групі читання (hostgroup 1)
-- Встановлення ліміту лагу 2 секунди
INSERT INTO mysql_servers (
    hostgroup_id, hostname, port, weight, max_connections, max_replication_lag
) VALUES 
    (1, '10.0.1.21', 3306, 100, 1000, 2),
    (1, '10.0.1.22', 3306, 100, 1000, 2),
    (1, '10.0.1.23', 3306, 100, 1000, 2);

-- Завантажити сервери в активний runtime та зафіксувати на диску
LOAD MYSQL SERVERS TO RUNTIME;
SAVE MYSQL SERVERS TO DISK;
