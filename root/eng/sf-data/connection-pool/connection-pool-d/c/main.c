#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <unistd.h>
#include <errno.h>
#include <poll.h>
#include <sys/socket.h>
#include <libpq-fe.h>

#define BASE_DELAY_MS 50
#define MAX_DELAY_MS 2000
#define MAX_RETRY_ATTEMPTS 5

typedef struct {
    PGconn *conn;
    char conninfo[256];
} DatabaseClient;

/* Неблокуюча перевірка працездатності TCP-сокета */
static bool is_connection_healthy(PGconn *conn) {
    if (!conn || PQstatus(conn) != CONNECTION_OK) {
        return false;
    }
    int socket_fd = PQsocket(conn);
    if (socket_fd < 0) return false;

    struct pollfd pfd = {
        .fd = socket_fd,
        .events = POLLIN | POLLRDHUP | POLLERR | POLLHUP,
        .revents = 0
    };

    int poll_res = poll(&pfd, 1, 0); // 0 мс — миттєва перевірка черги сокета в ядрі
    if (poll_res < 0) return false;
    if (poll_res > 0) {
        if (pfd.revents & (POLLERR | POLLHUP | POLLRDHUP)) {
            return false;
        }
        if (pfd.revents & POLLIN) {
            char probe_byte[1];
            ssize_t bytes_read = recv(socket_fd, probe_byte, 1, MSG_PEEK | MSG_DONTWAIT);
            if (bytes_read == 0) return false; // Віддалений сервер або пулер закрив TCP FIN
            if (bytes_read < 0 && errno != EAGAIN && errno != EWOULDBLOCK) return false;
        }
    }
    return true;
}

/* Відновлення зв'язку з експоненційним відступом та джитером */
static bool reconnect_to_pooler(DatabaseClient *client) {
    if (client->conn) {
        PQfinish(client->conn);
        client->conn = NULL;
    }

    int current_window_ms = BASE_DELAY_MS;
    for (int attempt = 1; attempt <= MAX_RETRY_ATTEMPTS; attempt++) {
        client->conn = PQconnectdb(client->conninfo);
        if (PQstatus(client->conn) == CONNECTION_OK) {
            return true;
        }

        PQfinish(client->conn);
        client->conn = NULL;

        // Випадковий джитер: Uniform(0, current_window_ms)
        int sleep_ms = rand() % (current_window_ms + 1);
        usleep((useconds_t)sleep_ms * 1000);

        current_window_ms *= 2;
        if (current_window_ms > MAX_DELAY_MS) {
            current_window_ms = MAX_DELAY_MS;
        }
    }
    return false;
}

DatabaseClient* db_client_init(const char *conninfo) {
    DatabaseClient *client = (DatabaseClient*)malloc(sizeof(DatabaseClient));
    if (!client) return NULL;
    
    strncpy(client->conninfo, conninfo, sizeof(client->conninfo) - 1);
    client->conninfo[sizeof(client->conninfo) - 1] = '\0';
    client->conn = NULL;

    if (!reconnect_to_pooler(client)) {
        free(client);
        return NULL;
    }
    return client;
}

void db_client_close(DatabaseClient *client) {
    if (!client) return;
    if (client->conn) PQfinish(client->conn);
    free(client);
}

/* Виконання атомарної транзакції через пулер */
bool db_execute_scoped_tx(DatabaseClient *client, const char *sql_query) {
    if (!is_connection_healthy(client->conn)) {
        if (!reconnect_to_pooler(client)) {
            return false;
        }
    }

    PGresult *res = PQexec(client->conn, "BEGIN");
    if (PQresultStatus(res) != PGRES_COMMAND_OK) {
        PQclear(res);
        return false;
    }
    PQclear(res);

    res = PQexec(client->conn, sql_query);
    if (PQresultStatus(res) != PGRES_COMMAND_OK && PQresultStatus(res) != PGRES_TUPLES_OK) {
        PQclear(res);
        PQexec(client->conn, "ROLLBACK");
        return false;
    }
    PQclear(res);

    res = PQexec(client->conn, "COMMIT");
    bool success = (PQresultStatus(res) == PGRES_COMMAND_OK);
    PQclear(res);
    return success;
}
