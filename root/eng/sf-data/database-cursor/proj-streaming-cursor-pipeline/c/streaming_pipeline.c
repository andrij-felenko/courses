/* streaming_pipeline.c — Потокова обробка через серверний курсор (C99 / libpq) */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <libpq-fe.h>

#define BATCH_SIZE 1000

typedef struct {
    unsigned long total_records;
    double total_amount;
} AggregationStats;

/* Перевірка статусу виконання команди та безпечне звільнення результату */
static bool check_command_status(PGconn *conn, PGresult *res, ExecStatusType expected) {
    if (PQresultStatus(res) != expected) {
        fprintf(stderr, "Помилка SQL: %s\n", PQerrorMessage(conn));
        PQclear(res);
        return false;
    }
    PQclear(res);
    return true;
}

/* Обробка одного завантаженого пакета рядків у пам'яті */
static void process_batch(PGresult *res, AggregationStats *stats) {
    int rows = PQntuples(res);
    int col_amount = PQfnumber(res, "amount");

    for (int i = 0; i < rows; ++i) {
        if (!PQgetisnull(res, i, col_amount)) {
            char *val_str = PQgetvalue(res, i, col_amount);
            double amount = strtod(val_str, NULL);
            stats->total_amount += amount;
            stats->total_records++;
        }
    }
}

int run_streaming_pipeline(const char *conninfo) {
    PGconn *conn = PQconnectdb(conninfo);
    if (PQstatus(conn) != CONNECTION_OK) {
        fprintf(stderr, "Не вдалося підключитися до бази даних: %s\n", PQerrorMessage(conn));
        PQfinish(conn);
        return 1;
    }

    AggregationStats stats = { .total_records = 0, .total_amount = 0.0 };

    /* 1. Відкриття транзакції: курсор існує в межах транзакційного блоку */
    PGresult *res = PQexec(conn, "BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;");
    if (!check_command_status(conn, res, PGRES_COMMAND_OK)) {
        PQfinish(conn);
        return 1;
    }

    /* 2. Оголошення однонаправленого серверного курсора */
    const char *decl_sql = 
        "DECLARE trans_cursor NO SCROLL CURSOR FOR "
        "SELECT id, user_id, amount, created_at FROM transactions WHERE status = 'COMPLETED';";
    res = PQexec(conn, decl_sql);
    if (!check_command_status(conn, res, PGRES_COMMAND_OK)) {
        PQexec(conn, "ROLLBACK;");
        PQfinish(conn);
        return 1;
    }

    char fetch_sql[64];
    snprintf(fetch_sql, sizeof(fetch_sql), "FETCH %d FROM trans_cursor;", BATCH_SIZE);

    /* 3. Ітеративна пакетна вибірка з константним споживанням RAM */
    bool has_more = true;
    while (has_more) {
        res = PQexec(conn, fetch_sql);
        if (PQresultStatus(res) != PGRES_TUPLES_OK) {
            fprintf(stderr, "Помилка під час FETCH: %s\n", PQerrorMessage(conn));
            PQclear(res);
            PQexec(conn, "ROLLBACK;");
            PQfinish(conn);
            return 1;
        }

        int fetched_count = PQntuples(res);
        if (fetched_count == 0) {
            has_more = false;
        } else {
            process_batch(res, &stats);
        }
        PQclear(res);
    }

    /* 4. Закриття курсора та фіксація транзакції */
    res = PQexec(conn, "CLOSE trans_cursor;");
    check_command_status(conn, res, PGRES_COMMAND_OK);

    res = PQexec(conn, "COMMIT;");
    check_command_status(conn, res, PGRES_COMMAND_OK);

    printf("Успішно опрацьовано: %lu рядків, загальна сума: %.2f\n", 
           stats.total_records, stats.total_amount);

    PQfinish(conn);
    return 0;
}
