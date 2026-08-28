/* client_failover_driver.c — Клієнтський автомат станів перепідключення до primary */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <time.h>

#define MAX_HOSTS 3
#define BASE_BACKOFF_MS 100
#define MAX_BACKOFF_MS 3000
#define MAX_RETRY_ATTEMPTS 10

typedef enum {
    STATE_DISCONNECTED,
    STATE_PROBING_HOSTS,
    STATE_CONNECTED_PRIMARY,
    STATE_BACKOFF_WAIT,
    STATE_FATAL_FAILURE
} client_state_t;

typedef struct {
    char host[64];
    uint16_t port;
    bool is_alive;
    bool is_read_only;
} db_host_node_t;

typedef struct {
    db_host_node_t hosts[MAX_HOSTS];
    size_t host_count;
    size_t active_host_idx;
    client_state_t state;
    uint32_t current_attempt;
} db_cluster_client_t;

/* Імітація перевірки вузла на доступність та режим Read-Write */
static bool mock_db_check_is_primary(const char* host, uint16_t port) {
    /* У реальній системі: надсилання запиту "SHOW transaction_read_only" через сокет */
    if (strcmp(host, "10.0.1.12") == 0) {
        return true; /* Вузол 2 став новим primary */
    }
    return false;
}

/* Обчислення випадкового експоненційного відступу (Full Jitter) */
static uint32_t calculate_backoff_ms(uint32_t attempt) {
    uint32_t max_sleep = BASE_BACKOFF_MS * (1U << (attempt > 6 ? 6 : attempt));
    if (max_sleep > MAX_BACKOFF_MS) {
        max_sleep = MAX_BACKOFF_MS;
    }
    return (uint32_t)(rand() % (max_sleep + 1));
}

void db_client_init(db_cluster_client_t* client) {
    client->host_count = 3;
    client->active_host_idx = 0;
    client->state = STATE_DISCONNECTED;
    client->current_attempt = 0;

    strncpy(client->hosts[0].host, "10.0.1.11", 64);
    client->hosts[0].port = 5432;
    strncpy(client->hosts[1].host, "10.0.1.12", 64);
    client->hosts[1].port = 5432;
    strncpy(client->hosts[2].host, "10.0.1.13", 64);
    client->hosts[2].port = 5432;
}

bool db_client_execute_query_with_failover(db_cluster_client_t* client, const char* sql) {
    while (client->state != STATE_FATAL_FAILURE) {
        switch (client->state) {
            case STATE_DISCONNECTED:
                client->state = STATE_PROBING_HOSTS;
                break;

            case STATE_PROBING_HOSTS: {
                bool found_primary = false;
                for (size_t i = 0; i < client->host_count; ++i) {
                    size_t idx = (client->active_host_idx + i) % client->host_count;
                    if (mock_db_check_is_primary(client->hosts[idx].host, client->hosts[idx].port)) {
                        client->active_host_idx = idx;
                        client->state = STATE_CONNECTED_PRIMARY;
                        client->current_attempt = 0;
                        found_primary = true;
                        fprintf(stdout, "[CLIENT] Успішно підключено до Primary: %s:%u\n",
                                client->hosts[idx].host, client->hosts[idx].port);
                        break;
                    }
                }
                if (!found_primary) {
                    client->state = STATE_BACKOFF_WAIT;
                }
                break;
            }

            case STATE_CONNECTED_PRIMARY:
                /* Імітація виконання транзакції */
                fprintf(stdout, "[CLIENT] Виконання SQL на primary (%s): %s\n",
                        client->hosts[client->active_host_idx].host, sql);
                return true;

            case STATE_BACKOFF_WAIT: {
                client->current_attempt++;
                if (client->current_attempt >= MAX_RETRY_ATTEMPTS) {
                    fprintf(stderr, "[CLIENT] Перевищено ліміт спроб! Кластер недоступний.\n");
                    client->state = STATE_FATAL_FAILURE;
                    return false;
                }
                uint32_t sleep_ms = calculate_backoff_ms(client->current_attempt);
                fprintf(stderr, "[CLIENT] Primary не знайдено. Спроба %u/%u. Очікування %u мс...\n",
                        client->current_attempt, MAX_RETRY_ATTEMPTS, sleep_ms);
                usleep(sleep_ms * 1000);
                client->state = STATE_PROBING_HOSTS;
                break;
            }

            case STATE_FATAL_FAILURE:
                return false;
        }
    }
    return false;
}
