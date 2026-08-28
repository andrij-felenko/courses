// Пакетне оновлення балансів через багаторазовий запуск одного виразу
int batch_update_balances(sqlite3 *db, const int64_t *ids, const double *amounts, size_t count) {
    const char *sql = "UPDATE accounts SET balance = balance + ? WHERE id = ?;";
    sqlite3_stmt *stmt = NULL;

    if (sqlite3_prepare_v2(db, sql, -1, &stmt, NULL) != SQLITE_OK) {
        return -1;
    }

    // Відкриття транзакції для пакетного запису
    sqlite3_exec(db, "BEGIN TRANSACTION;", NULL, NULL, NULL);

    for (size_t i = 0; i < count; i++) {
        // Зв'язування нових параметрів
        sqlite3_bind_double(stmt, 1, amounts[i]);
        sqlite3_bind_int64(stmt, 2, ids[i]);

        if (sqlite3_step(stmt) != SQLITE_DONE) {
            sqlite3_finalize(stmt);
            sqlite3_exec(db, "ROLLBACK;", NULL, NULL, NULL);
            return -1;
        }

        // Скидання стану виконання для наступної ітерації (без перепарсингу!)
        sqlite3_reset(stmt);
        sqlite3_clear_bindings(stmt);
    }

    sqlite3_exec(db, "COMMIT;", NULL, NULL, NULL);
    sqlite3_finalize(stmt);
    return 0;
}
