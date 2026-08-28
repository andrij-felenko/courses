/* Порівняльна реалізація менеджера з'єднань мовою C (POSIX) */
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    char endpoint[64];
    int socket_id;
} DatabaseConnectionC;

typedef struct {
    char host[48];
    int port;
    DatabaseConnectionC* connection;
    pthread_mutex_t mutex;
    int is_initialized;
} ResilientConnectionManagerC;

void init_manager_c(ResilientConnectionManagerC* mgr, const char* host, int port) {
    strncpy(mgr->host, host, 47);
    mgr->port = port;
    mgr->connection = NULL;
    pthread_mutex_init(&mgr->mutex, NULL);
    mgr->is_initialized = 0;
}

int execute_c(ResilientConnectionManagerC* mgr, const char* sql, int thread_id) {
    /* Наївна C-реалізація вимагає блокування м'ютекса навіть після ініціалізації */
    pthread_mutex_lock(&mgr->mutex);
    if (!mgr->is_initialized) {
        printf(">>> [C INIT] Ініціалізація з'єднання...\n");
        mgr->connection = (DatabaseConnectionC*)malloc(sizeof(DatabaseConnectionC));
        if (mgr->connection) {
            snprintf(mgr->connection->endpoint, 63, "%s:%d", mgr->host, mgr->port);
            mgr->connection->socket_id = 2042;
            mgr->is_initialized = 1;
            printf(">>> [C INIT] Успішно підключено.\n");
        }
    }
    pthread_mutex_unlock(&mgr->mutex);

    if (mgr->connection) {
        printf("[C Потік %d] Запит '%s' виконано через сокет #%d\n",
               thread_id, sql, mgr->connection->socket_id);
        return 0;
    }
    return -1;
}
