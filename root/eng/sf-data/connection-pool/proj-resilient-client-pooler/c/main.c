#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <unistd.h>
#include <errno.h>
#include <poll.h>
#include <sys/socket.h>
#include <libpq-fe.h>

#define BASE_BACKOFF_MS 50
#define MAX_BACKOFF_MS 2000
#define MAX_RETRIES 5

typedef struct {
    PGconn *conn;
    char conninfo[256];
} DbClient;

/* Неблокуюча перевірка стану TCP-дескриптора в ядрі ОС */
static bool is_socket_alive(PGconn *conn) {
    if (!conn || PQstatus(conn) != CONNECTION_OK) {
        return false;
    }
    int fd = PQsocket(conn);
    if (fd < 0) return false;

    struct pollfd pfd = { 
        .fd = fd, 
        .events = POLLIN | POLLRDHUP | POLLERR | POLLHUP, 
        .revents = 0 
    };

    int ret = poll(&pfd, 1, 0); // 0 мс — миттєве неблокуюче опитування буферів ядра
    if (ret < 0) return false;
    if (ret > 0) {
        if (pfd.revents & (POLLERR | POLLHUP | POLLRDHUP)) {
            return false;
        }
        if (pfd.revents & POLLIN) {
            char buf[1];
            ssize_t n = recv(fd, buf, sizeof(buf), MSG_PEEK | MSG_DONTWAIT);
            if (n == 0) return false; // Отримано FIN від пулера (EOF)
            if (n < 0 && errno != EAGAIN && errno != EWOULDBLOCK) return false;
        }
    }
    return true;
}

/* Відновлення з'єднання з експоненційним відступом та джитером */
static bool db_reconnect(DbClient *client) {
    if (client->conn) {
        PQfinish(client->conn);
        client->conn = NULL;
    }

    int delay_ms = BASE_BACKOFF_MS;
    for (int attempt = 1; attempt <= MAX_RETRIES; attempt++) {
        client->conn = PQconnectdb(client->conninfo);
        if (PQstatus(client->conn) == CONNECTION_OK) {
            return true;
        }

        PQfinish(client->conn);
        client->conn = NULL;

        // Full Jitter = random(0, delay_ms)
        int jitter = rand() % (delay_ms + 1);
        usleep((useconds_t)jitter * 1000);

        delay_ms *= 2;
        if (delay_ms > MAX_BACKOFF_MS) delay_ms = MAX_BACKOFF_MS;
    }
    return false;
}

DbClient* db_client_create(const char *conninfo) {
    DbClient *client = (DbClient*)malloc(sizeof(DbClient));
    if (!client) return NULL;
    strncpy(client->conninfo, conninfo, sizeof(client->conninfo) - 1);
    client->conninfo[sizeof(client->conninfo) - 1] = '\0';
    client->conn = NULL;

    if (!db_reconnect(client)) {
        free(client);
        return NULL;
    }
    return client;
}

void db_client_destroy(DbClient *client) {
    if (!client) return;
    if (client->conn) PQfinish(client->conn);
    free(client);
}

/* Виконання атомарної транзакції через транзакційний пулер */
bool db_execute_transaction(DbClient *client, const char *sql_update, const char *sql_log) {
    if (!is_socket_alive(client->conn)) {
        if (!db_reconnect(client)) return false;
    }

    PGresult *res = PQexec(client->conn, "BEGIN");
    if (PQresultStatus(res) != PGRES_COMMAND_OK) {
        PQclear(res);
        return false;
    }
    PQclear(res);

    res = PQexec(client->conn, sql_update);
    if (PQresultStatus(res) != PGRES_COMMAND_OK && PQresultStatus(res) != PGRES_TUPLES_OK) {
        PQclear(res);
        PQexec(client->conn, "ROLLBACK");
        return false;
    }
    PQclear(res);

    res = PQexec(client->conn, sql_log);
    if (PQresultStatus(res) != PGRES_COMMAND_OK && PQresultStatus(res) != PGRES_TUPLES_OK) {
        PQclear(res);
        PQexec(client->conn, "ROLLBACK");
        return false;
    }
    PQclear(res);

    res = PQexec(client->conn, "COMMIT");
    bool ok = (PQresultStatus(res) == PGRES_COMMAND_OK);
    PQclear(res);
    return ok;
}
