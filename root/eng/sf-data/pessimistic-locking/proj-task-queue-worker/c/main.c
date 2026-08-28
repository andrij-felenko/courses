#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <libpq-fe.h>

#define MAX_PAYLOAD_LEN 1024

typedef struct {
    long long id;
    char payload[MAX_PAYLOAD_LEN];
    int attempts;
} task_item_t;

static int fetch_and_lock_task(PGconn *conn, task_item_t *task) {
    PGresult *res = PQexec(conn, "BEGIN;");
    if (PQresultStatus(res) != PGRES_COMMAND_OK) {
        PQclear(res);
        return -1;
    }
    PQclear(res);

    const char *query = 
        "SELECT id, payload, attempts "
        "FROM task_queue "
        "WHERE status = 'pending' "
        "ORDER BY id ASC "
        "LIMIT 1 "
        "FOR UPDATE SKIP LOCKED;";

    res = PQexec(conn, query);
    if (PQresultStatus(res) != PGRES_TUPLES_OK) {
        PQclear(res);
        PQexec(conn, "ROLLBACK;");
        return -1;
    }

    int rows = PQntuples(res);
    if (rows == 0) {
        PQclear(res);
        PQexec(conn, "COMMIT;");
        return 0; // Черга порожня
    }

    task->id = atoll(PQgetvalue(res, 0, 0));
    strncpy(task->payload, PQgetvalue(res, 0, 1), sizeof(task->payload) - 1);
    task->payload[sizeof(task->payload) - 1] = '\0';
    task->attempts = atoi(PQgetvalue(res, 0, 2));

    PQclear(res);
    return 1; // Завдання успішно захоплено
}

static int complete_task(PGconn *conn, long long task_id) {
    char query[256];
    snprintf(query, sizeof(query),
             "UPDATE task_queue SET status = 'completed', updated_at = NOW() WHERE id = %lld;",
             task_id);

    PGresult *res = PQexec(conn, query);
    if (PQresultStatus(res) != PGRES_COMMAND_OK) {
        PQclear(res);
        PQexec(conn, "ROLLBACK;");
        return -1;
    }
    PQclear(res);

    res = PQexec(conn, "COMMIT;");
    PQclear(res);
    return 0;
}

void run_worker(const char *conninfo) {
    PGconn *conn = PQconnectdb(conninfo);
    if (PQstatus(conn) != CONNECTION_OK) {
        PQfinish(conn);
        return;
    }

    while (1) {
        task_item_t task;
        int status = fetch_and_lock_task(conn, &task);
        if (status > 0) {
            // Обробка корисного навантаження
            complete_task(conn, task.id);
        } else if (status == 0) {
            usleep(100000); // 100 мс паузи перед наступним опитуванням
        } else {
            usleep(500000); // Пауза при помилці бази
        }
    }

    PQfinish(conn);
}
