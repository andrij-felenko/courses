#include <stdio.h>
#include <sqlite3.h>

/* Безпечна вибірка балансу користувача мовою C */
int get_user_balance(sqlite3 *db, int user_id, double *out_balance) {
    sqlite3_stmt *stmt = NULL;
    const char *sql = "SELECT balance FROM accounts WHERE user_id = ?;";
    int rc;

    /* 1. Компіляція синтаксичного дерева */
    rc = sqlite3_prepare_v2(db, sql, -1, &stmt, NULL);
    if (rc != SQLITE_OK) {
        fprintf(stderr, "Помилка prepare: %s\n", sqlite3_errmsg(db));
        return rc;
    }

    /* 2. Прив'язка бінарного параметра */
    sqlite3_bind_int(stmt, 1, user_id);

    /* 3. Ітерація по курсору */
    rc = sqlite3_step(stmt);
    if (rc == SQLITE_ROW) {
        *out_balance = sqlite3_column_double(stmt, 0);
        sqlite3_finalize(stmt);
        return SQLITE_OK;
    }

    sqlite3_finalize(stmt);
    return (rc == SQLITE_DONE) ? SQLITE_NOTFOUND : rc;
}
