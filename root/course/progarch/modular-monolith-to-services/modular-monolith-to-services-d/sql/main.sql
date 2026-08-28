-- Ізоляція прав на рівні користувачів PostgreSQL
CREATE SCHEMA schema_telemetry;
ALTER TABLE telemetry_readings SET SCHEMA schema_telemetry;

-- Створення ізольованого користувача для нового мікросервісу
CREATE USER telemetry_service_user WITH PASSWORD 'secure_pass';
GRANT ALL PRIVILEGES ON SCHEMA schema_telemetry TO telemetry_service_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA schema_telemetry TO telemetry_service_user;

-- Відкликання прав у користувача моноліта на таблиці телеметрії
REVOKE ALL ON SCHEMA schema_telemetry FROM monolith_user;
