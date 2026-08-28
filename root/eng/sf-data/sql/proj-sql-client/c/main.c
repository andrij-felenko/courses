#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <sqlite3.h>

typedef struct {
    int64_t id;
    char name[64];
    int64_t balance_cents;
} Account;

/* Виконання транзакційного переказу коштів між рахунками */
int transfer_funds(sqlite3 *db, int64_t from_id, int64_t to_id, int64_t amount_cents) {
    sqlite3_stmt *stmt_debit = NULL;
    sqlite3_stmt *stmt_credit = NULL;
    char *err_msg = NULL;
    int rc = SQLITE_OK;

    /* 1. Початок ексклюзивної транзакції */
    rc = sqlite3_exec(db, "BEGIN IMMEDIATE TRANSACTION;", NULL, NULL, &err_msg);
    if (rc != SQLITE_OK) {
        fprintf(stderr, "Помилка відкриття транзакції: %s\n", err_msg);
        sqlite3_free(err_msg);
        return rc;
    }

    /* 2. Підготовка виразів для списання та зарахування */
    const char *sql_debit = "UPDATE accounts SET balance_cents = balance_cents - ? "
                            "WHERE id = ? AND balance_cents >= ?;";
    const char *sql_credit = "UPDATE accounts SET balance_cents = balance_cents + ? "
                             "WHERE id = ?;";

    rc = sqlite3_prepare_v2(db, sql_debit, -1, &stmt_debit, NULL);
    if (rc != SQLITE_OK) goto rollback;

    rc = sqlite3_prepare_v2(db, sql_credit, -1, &stmt_credit, NULL);
    if (rc != SQLITE_OK) goto rollback;

    /* 3. Прив'язка параметрів до виразу списання */
    sqlite3_bind_int64(stmt_debit, 1, amount_cents);
    sqlite3_bind_int64(stmt_debit, 2, from_id);
    sqlite3_bind_int64(stmt_debit, 3, amount_cents);

    rc = sqlite3_step(stmt_debit);
    if (rc != SQLITE_DONE) goto rollback;

    /* Перевірка, чи було оновлено рядок (наявність коштів) */
    if (sqlite3_changes(db) == 0) {
        fprintf(stderr, "Недостатньо коштів або рахунок не знайдено: id=%lld\n", (long long)from_id);
        goto rollback;
    }

    /* 4. Прив'язка параметрів до виразу зарахування */
    sqlite3_bind_int64(stmt_credit, 1, amount_cents);
    sqlite3_bind_int64(stmt_credit, 2, to_id);

    rc = sqlite3_step(stmt_credit);
    if (rc != SQLITE_DONE) goto rollback;

    if (sqlite3_changes(db) == 0) {
        fprintf(stderr, "Рахунок отримувача не знайдено: id=%lld\n", (long long)to_id);
        goto rollback;
    }

    /* 5. Фіксація транзакції */
    rc = sqlite3_exec(db, "COMMIT TRANSACTION;", NULL, NULL, &err_msg);
    if (rc != SQLITE_OK) {
        fprintf(stderr, "Помилка COMMIT: %s\n", err_msg);
        sqlite3_free(err_msg);
        goto rollback;
    }

    sqlite3_finalize(stmt_debit);
    sqlite3_finalize(stmt_credit);
    return SQLITE_OK;

rollback:
    sqlite3_exec(db, "ROLLBACK TRANSACTION;", NULL, NULL, NULL);
    if (stmt_debit) sqlite3_finalize(stmt_debit);
    if (stmt_credit) sqlite3_finalize(stmt_credit);
    return SQLITE_ERROR;
}

/* Безпечна параметризована вибірка даних */
int query_account(sqlite3 *db, int64_t account_id, Account *out_account) {
    sqlite3_stmt *stmt = NULL;
    const char *sql = "SELECT id, name, balance_cents FROM accounts WHERE id = ?;";

    int rc = sqlite3_prepare_v2(db, sql, -1, &stmt, NULL);
    if (rc != SQLITE_OK) {
        fprintf(stderr, "Помилка підготовки виразу: %s\n", sqlite3_errmsg(db));
        return rc;
    }

    sqlite3_bind_int64(stmt, 1, account_id);

    rc = sqlite3_step(stmt);
    if (rc == SQLITE_ROW) {
        out_account->id = sqlite3_column_int64(stmt, 0);
        const unsigned char *text = sqlite3_column_text(stmt, 1);
        snprintf(out_account->name, sizeof(out_account->name), "%s", text ? (const char*)text : "");
        out_account->balance_cents = sqlite3_column_int64(stmt, 2);
        sqlite3_finalize(stmt);
        return SQLITE_OK;
    }

    sqlite3_finalize(stmt);
    return SQLITE_NOTFOUND;
}
