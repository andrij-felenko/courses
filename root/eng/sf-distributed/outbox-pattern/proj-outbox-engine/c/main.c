#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <signal.h>
#include <unistd.h>
#include <libpq-fe.h>

#define BATCH_SIZE 50
#define POLL_INTERVAL_USEC 200000 // 200 мс

static volatile sig_atomic_t g_running = 1;

void handle_signal(int sig) {
    (void)sig;
    g_running = 0;
}

// Імітація надійного відправлення повідомлення у брокер (Kafka/RabbitMQ)
bool mock_broker_publish(const char *topic, const char *key, const char *payload) {
    if (!topic || !key || !payload) return false;
    // У реальній системі тут викликається rd_kafka_producev() з очікуванням черги
    return true; 
}

// Обробка однієї пачки подій у межах транзакції
int process_outbox_batch(PGconn *conn) {
    PGresult *res = PQexec(conn, "BEGIN;");
    if (PQresultStatus(res) != PGRES_COMMAND_OK) {
        PQclear(res);
        return -1;
    }
    PQclear(res);

    // Блокуємо та вибираємо пачку, пропускаючи вже зайняті рядки
    const char *fetch_sql = 
        "SELECT id, aggregate_type, aggregate_id, payload "
        "FROM outbox "
        "ORDER BY created_at ASC "
        "LIMIT $1 "
        "FOR UPDATE SKIP LOCKED;";

    const char *param_values[1];
    char batch_str[16];
    snprintf(batch_str, sizeof(batch_str), "%d", BATCH_SIZE);
    param_values[0] = batch_str;

    res = PQexecParams(conn, fetch_sql, 1, NULL, param_values, NULL, NULL, 0);
    if (PQresultStatus(res) != PGRES_TUPLES_OK) {
        PQclear(res);
        PQexec(conn, "ROLLBACK;");
        return -1;
    }

    int rows = PQntuples(res);
    if (rows == 0) {
        PQclear(res);
        PQexec(conn, "COMMIT;");
        return 0; // Немає нових подій
    }

    bool batch_ok = true;
    for (int i = 0; i < rows; ++i) {
        const char *id = PQgetvalue(res, i, 0);
        const char *topic = PQgetvalue(res, i, 1);
        const char *key = PQgetvalue(res, i, 2);
        const char *payload = PQgetvalue(res, i, 3);

        if (!mock_broker_publish(topic, key, payload)) {
            batch_ok = false;
            break;
        }

        // Видаляємо оброблений рядок у тій самій транзакції
        const char *del_sql = "DELETE FROM outbox WHERE id = $1;";
        const char *del_params[1] = { id };
        PGresult *del_res = PQexecParams(conn, del_sql, 1, NULL, del_params, NULL, NULL, 0);
        if (PQresultStatus(del_res) != PGRES_COMMAND_OK) {
            PQclear(del_res);
            batch_ok = false;
            break;
        }
        PQclear(del_res);
    }

    PQclear(res);

    if (batch_ok) {
        res = PQexec(conn, "COMMIT;");
        if (PQresultStatus(res) == PGRES_COMMAND_OK) {
            PQclear(res);
            return rows;
        }
        PQclear(res);
    }

    PQexec(conn, "ROLLBACK;");
    return -1;
}

int main(void) {
    signal(SIGINT, handle_signal);
    signal(SIGTERM, handle_signal);

    const char *conninfo = "host=localhost port=5432 dbname=shop user=postgres password=secret";
    PGconn *conn = PQconnectdb(conninfo);

    if (PQstatus(conn) != CONNECTION_OK) {
        PQfinish(conn);
        return 1;
    }

    while (g_running) {
        int processed = process_outbox_batch(conn);
        if (processed == 0) {
            usleep(POLL_INTERVAL_USEC);
        } else if (processed < 0) {
            usleep(POLL_INTERVAL_USEC * 2); // Пауза при помилці
        }
    }

    PQfinish(conn);
    return 0;
}
