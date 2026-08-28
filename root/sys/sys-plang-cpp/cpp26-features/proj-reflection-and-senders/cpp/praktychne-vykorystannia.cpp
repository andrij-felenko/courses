struct SensorTelemetryRow {
    int64_t id;
    std::string device_uuid;
    double temperature;
    double pressure;
    int32_t battery_percent;
};

void run_database_schema_demo() {
    // Рядок створюється компілятором без динамічних алокацій під час запуску
    constexpr auto schema_query = generate_create_table_sql<SensorTelemetryRow>("telemetry_records");
    constexpr auto insert_query = generate_insert_sql<SensorTelemetryRow>("telemetry_records");

    std::cout << "[SQL SCHEMA] " << schema_query << std::endl;
    std::cout << "[SQL INSERT] " << insert_query << std::endl;
}
