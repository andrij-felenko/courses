#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <libpq-fe.h>

#define MAX_RETRIES 3
#define BASE_BACKOFF_US 50000 // 50 мс

static int execute_command(PGconn *conn, const char *sql) {
    PGresult *res = PQexec(conn, sql);
    ExecStatusType status = PQresultStatus(res);
    if (status != PGRES_COMMAND_OK && status != PGRES_TUPLES_OK) {
        PQclear(res);
        return -1;
    }
    PQclear(res);
    return 0;
}

// Безпечний переказ коштів із канонічним порядком блокування
int transfer_funds_pessimistic(PGconn *conn, long long from_id, long long to_id, double amount) {
    // Встановлюємо жорсткий сесійний ліміт очікування замка в 2 секунди
    if (execute_command(conn, "SET lock_timeout = '2s';") != 0) {
        return -1;
    }

    // Канонічне впорядкування: завжди спочатку блокуємо менший ID
    long long first_id = (from_id < to_id) ? from_id : to_id;
    long long second_id = (from_id < to_id) ? to_id : from_id;

    for (int attempt = 0; attempt < MAX_RETRIES; attempt++) {
        if (execute_command(conn, "BEGIN;") != 0) {
            return -1;
        }

        char query[512];
        snprintf(query, sizeof(query),
                 "SELECT id, balance FROM accounts WHERE id IN (%lld, %lld) ORDER BY id ASC FOR UPDATE;",
                 first_id, second_id);

        PGresult *res = PQexec(conn, query);
        if (PQresultStatus(res) != PGRES_TUPLES_OK) {
            char *sqlstate = PQresultErrorField(res, PG_DIAG_SQLSTATE);
            int is_deadlock_or_timeout = 0;
            if (sqlstate && (strcmp(sqlstate, "40P01") == 0 || strcmp(sqlstate, "55P03") == 0 || strcmp(sqlstate, "57014") == 0)) {
                is_deadlock_or_timeout = 1;
            }
            PQclear(res);
            execute_command(conn, "ROLLBACK;");

            if (is_deadlock_or_timeout && attempt < MAX_RETRIES - 1) {
                // Експоненційне випадкове запізнення перед повтором
                int sleep_time = BASE_BACKOFF_US * (1 << attempt) + (rand() % 20000);
                usleep(sleep_time);
                continue;
            }
            return -1;
        }

        if (PQntuples(res) != 2) {
            PQclear(res);
            execute_command(conn, "ROLLBACK;");
            return -2; // Один із рахунків не знайдено
        }

        double balance_from = 0.0;
        for (int i = 0; i < 2; i++) {
            long long id = atoll(PQgetvalue(res, i, 0));
            if (id == from_id) {
                balance_from = atof(PQgetvalue(res, i, 1));
            }
        }
        PQclear(res);

        if (balance_from < amount) {
            execute_command(conn, "ROLLBACK;");
            return -3; // Недостатньо коштів на балансі
        }

        // Оновлення балансів під захистом утримуваних X-locks
        snprintf(query, sizeof(query),
                 "UPDATE accounts SET balance = balance - %f WHERE id = %lld; "
                 "UPDATE accounts SET balance = balance + %f WHERE id = %lld;",
                 amount, from_id, amount, to_id);

        if (execute_command(conn, query) != 0) {
            execute_command(conn, "ROLLBACK;");
            return -1;
        }

        if (execute_command(conn, "COMMIT;") == 0) {
            return 0; // Успішне завершення переказу
        }
    }
    return -4; // Вичерпано всі спроби повтору
}
