auto stmt = db.prepare(R"(
    UPDATE climate_zones
    SET target_temperature = :temp, version = version + 1
    WHERE id = :id AND version = :expected_version
)");

stmt.bind(":temp", newTemperature);
stmt.bind(":id", zoneId);
stmt.bind(":expected_version", expectedVersion);

stmt.execute();

// Драйвер повертає кількість реально модифікованих рядків
const int affectedRows = db.changes();
if (affectedRows == 0) {
    // Втрата оновлення: стан було змінено іншим потоком
    return SaveStatus::ConcurrencyConflict;
}
