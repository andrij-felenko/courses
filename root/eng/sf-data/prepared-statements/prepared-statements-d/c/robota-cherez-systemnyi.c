#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sqlite3.h>

// Приклад безпечної роботи з підготовленим виразом у SQLite на чистому C
int query_user_balance(sqlite3 *db, int64_t user_id, double *out_balance) {
    const char *sql = "SELECT balance FROM accounts WHERE id = ?;";
    sqlite3_stmt *stmt = NULL;

    // 1. Компіляція шаблону запиту в байт-код VDBE
    int rc = sqlite3_prepare_v2(db, sql, -1, &stmt, NULL);
    if (rc != SQLITE_OK) {
        fprintf(stderr, "Помилка підготовки виразу: %s\n", sqlite3_errmsg(db));
        return -1;
    }

    // 2. Зв'язування параметра за індексом 1 (індексація починається з 1)
    sqlite3_bind_int64(stmt, 1, user_id);

    // 3. Покрокове виконання скомпільованого байт-коду
    rc = sqlite3_step(stmt);
    if (rc == SQLITE_ROW) {
        *out_balance = sqlite3_column_double(stmt, 0);
        rc = SQLITE_OK;
    } else if (rc == SQLITE_DONE) {
        // Рядок не знайдено
        rc = SQLITE_NOTFOUND;
    } else {
        fprintf(stderr, "Помилка виконання виразу: %s\n", sqlite3_errmsg(db));
        rc = -1;
    }

    // 4. Обов'язкове звільнення ресурсів виразу
    sqlite3_finalize(stmt);
    return rc;
}
