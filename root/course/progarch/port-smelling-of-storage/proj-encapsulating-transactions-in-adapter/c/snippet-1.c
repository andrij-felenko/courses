sqlite3_stmt *stmt;
sqlite3_prepare_v2(db, 
    "UPDATE climate_zones SET target_temperature = ?, version = version + 1 WHERE id = ? AND version = ?", 
    -1, &stmt, NULL);

sqlite3_bind_double(stmt, 1, new_temperature);
sqlite3_bind_text(stmt, 2, zone_id, -1, SQLITE_STATIC);
sqlite3_bind_int(stmt, 3, expected_version);

sqlite3_step(stmt);
sqlite3_finalize(stmt);

// Перевірка кількості змінених рядків через sqlite3_changes
int affected_rows = sqlite3_changes(db);
if (affected_rows == 0) {
    // Жодного рядка не змінено: відбулася колізія оптимістичного блокування
    return CONCURRENCY_CONFLICT;
}
