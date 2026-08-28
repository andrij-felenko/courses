/* cursor_stream_processor.c — Потокова обробка через серверний курсор мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <libpq-fe.h>

#define CHUNK_SIZE 1000

typedef struct {
    unsigned long count;
    double sum;
} StreamResult;

static bool exec_statement(PGconn *conn, const char *sql) {
    PGresult *res = PQexec(conn, sql);
    if (PQresultStatus(res) != PGRES_COMMAND_OK) {
        fprintf(stderr, "Помилка виконання SQL [%s]: %s\n", sql, PQerrorMessage(conn));
        PQclear(res);
        return false;
    }
    PQclear(res);
    return true;
}

int process_large_dataset_c(const char *conninfo, StreamResult *out) {
    PGconn *conn = PQconnectdb(conninfo);
    if (PQstatus(conn) != CONNECTION_OK) {
        fprintf(stderr, "Збій підключення: %s\n", PQerrorMessage(conn));
        PQfinish(conn);
        return -1;
    }

    out->count = 0;
    out->sum = 0.0;

    /* 1. Старт транзакції з рівнем ізоляції знімка */
    if (!exec_statement(conn, "BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;")) {
        PQfinish(conn);
        return -1;
    }

    /* 2. Створення однонаправленого потокового курсора */
    const char *decl_query = 
        "DECLARE trans_cur NO SCROLL CURSOR FOR "
        "SELECT amount FROM transactions WHERE status = 'SUCCESS';";
    if (!exec_statement(conn, decl_query)) {
        exec_statement(conn, "ROLLBACK;");
        PQfinish(conn);
        return -1;
    }

    char fetch_cmd[64];
    snprintf(fetch_cmd, sizeof(fetch_cmd), "FETCH %d FROM trans_cur;", CHUNK_SIZE);

    /* 3. Циклічне вичитування з фіксованим розміром буфера */
    while (true) {
        PGresult *res = PQexec(conn, fetch_cmd);
        if (PQresultStatus(res) != PGRES_TUPLES_OK) {
            fprintf(stderr, "Помилка вибірки FETCH: %s\n", PQerrorMessage(conn));
            PQclear(res);
            exec_statement(conn, "ROLLBACK;");
            PQfinish(conn);
            return -1;
        }

        int rows = PQntuples(res);
        if (rows == 0) {
            PQclear(res);
            break; /* Досягнуто кінця результуючого набору */
        }

        for (int i = 0; i < rows; ++i) {
            if (!PQgetisnull(res, i, 0)) {
                out->sum += strtod(PQgetvalue(res, i, 0), NULL);
                out->count++;
            }
        }
        PQclear(res);
    }

    /* 4. Закриття порталу та фіксація транзакції */
    exec_statement(conn, "CLOSE trans_cur;");
    exec_statement(conn, "COMMIT;");

    PQfinish(conn);
    return 0;
}
