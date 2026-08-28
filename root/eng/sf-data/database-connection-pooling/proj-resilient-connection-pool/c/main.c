#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include <errno.h>
#include <pthread.h>
#include <unistd.h>

/* Імітація дескриптора мережевого сокета бази даних */
typedef struct {
    int socket_fd;
    uint64_t created_at_ms;
    uint64_t last_used_at_ms;
    bool is_valid;
} db_connection_t;

/* Структура активної оренди для детекції витоків */
typedef struct {
    db_connection_t* conn;
    pthread_t owner_thread;
    uint64_t borrowed_at_ms;
    bool in_use;
} lease_slot_t;

/* Конфігурація пулу */
typedef struct {
    size_t capacity;
    uint64_t acquire_timeout_ms;
    uint64_t idle_validation_timeout_ms;
    uint64_t max_lifetime_ms;
    uint64_t leak_threshold_ms;
} pool_config_t;

/* Головна структура пулу з'єднань */
typedef struct {
    pool_config_t config;
    db_connection_t** idle_ring;
    size_t ring_head;
    size_t ring_tail;
    size_t idle_count;

    lease_slot_t* lease_table;
    size_t active_leases;

    pthread_mutex_t lock;
    pthread_cond_t not_empty_cond;
    pthread_cond_t drain_cond;

    bool is_shutdown;
    pthread_t watchdog_thread;
    bool watchdog_running;
} connection_pool_t;

static uint64_t get_time_monotonic_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000ULL + (uint64_t)ts.tv_nsec / 1000000ULL;
}

/* Імітація створення нового TCP/TLS сокета до СУБД */
static db_connection_t* db_connection_create(void) {
    db_connection_t* conn = (db_connection_t*)malloc(sizeof(db_connection_t));
    if (!conn) return NULL;
    static int fake_fd_counter = 100;
    conn->socket_fd = ++fake_fd_counter;
    conn->created_at_ms = get_time_monotonic_ms();
    conn->last_used_at_ms = conn->created_at_ms;
    conn->is_valid = true;
    return conn;
}

/* Імітація перевірки сокета (ping / SELECT 1) */
static bool db_connection_validate(db_connection_t* conn) {
    if (!conn || conn->socket_fd <= 0) return false;
    /* У реальній системі тут надсилається 1-байтовий ping або перевіряється сокет через poll(POLLIN) */
    return conn->is_valid;
}

static void db_connection_destroy(db_connection_t* conn) {
    if (!conn) return;
    if (conn->socket_fd > 0) {
        close(conn->socket_fd);
        conn->socket_fd = -1;
    }
    free(conn);
}

/* Вартовий потік перевірки витоків та застарілих з'єднань */
static void* pool_watchdog_loop(void* arg) {
    connection_pool_t* pool = (connection_pool_t*)arg;

    while (true) {
        usleep(500000); /* перевірка двічі на секунду */

        pthread_mutex_lock(&pool->lock);
        if (pool->is_shutdown && pool->active_leases == 0) {
            pthread_mutex_unlock(&pool->lock);
            break;
        }

        uint64_t now = get_time_monotonic_ms();

        /* Детекція витоків активних оренд */
        for (size_t i = 0; i < pool->config.capacity; ++i) {
            if (pool->lease_table[i].in_use) {
                uint64_t duration = now - pool->lease_table[i].borrowed_at_ms;
                if (duration > pool->config.leak_threshold_ms) {
                    fprintf(stderr, "[ПОПЕРЕДЖЕННЯ: ВИТОК З'ЄДНАННЯ] Сокет fd=%d утримується потоком %lu вже %lu мс!\n",
                            pool->lease_table[i].conn->socket_fd,
                            (unsigned long)pool->lease_table[i].owner_thread,
                            (unsigned long)duration);
                }
            }
        }

        pthread_mutex_unlock(&pool->lock);
    }
    return NULL;
}

connection_pool_t* connection_pool_create(pool_config_t cfg) {
    connection_pool_t* pool = (connection_pool_t*)calloc(1, sizeof(connection_pool_t));
    if (!pool) return NULL;

    pool->config = cfg;
    pool->idle_ring = (db_connection_t**)malloc(sizeof(db_connection_t*) * cfg.capacity);
    pool->lease_table = (lease_slot_t*)calloc(cfg.capacity, sizeof(lease_slot_t));

    if (!pool->idle_ring || !pool->lease_table) {
        free(pool->idle_ring);
        free(pool->lease_table);
        free(pool);
        return NULL;
    }

    pthread_mutex_init(&pool->lock, NULL);
    pthread_cond_init(&pool->not_empty_cond, NULL);
    pthread_cond_init(&pool->drain_cond, NULL);

    /* Попереднє наповнення пулу з'єднаннями */
    for (size_t i = 0; i < cfg.capacity; ++i) {
        db_connection_t* conn = db_connection_create();
        if (conn) {
            pool->idle_ring[pool->ring_tail] = conn;
            pool->ring_tail = (pool->ring_tail + 1) % cfg.capacity;
            pool->idle_count++;
        }
    }

    pool->is_shutdown = false;
    pool->watchdog_running = true;
    pthread_create(&pool->watchdog_thread, NULL, pool_watchdog_loop, pool);

    return pool;
}

/* Оренда з'єднання з дедлайном */
db_connection_t* connection_pool_acquire(connection_pool_t* pool) {
    if (!pool) return NULL;

    struct timespec deadline;
    clock_gettime(CLOCK_REALTIME, &deadline);
    deadline.tv_sec += pool->config.acquire_timeout_ms / 1000ULL;
    deadline.tv_nsec += (pool->config.acquire_timeout_ms % 1000ULL) * 1000000ULL;
    if (deadline.tv_nsec >= 1000000000L) {
        deadline.tv_sec += 1;
        deadline.tv_nsec -= 1000000000L;
    }

    pthread_mutex_lock(&pool->lock);

    while (pool->idle_count == 0 && !pool->is_shutdown) {
        int rc = pthread_cond_timedwait(&pool->not_empty_cond, &pool->lock, &deadline);
        if (rc == ETIMEDOUT) {
            pthread_mutex_unlock(&pool->lock);
            return NULL; /* вичерпано бюджет очікування */
        }
    }

    if (pool->is_shutdown) {
        pthread_mutex_unlock(&pool->lock);
        return NULL;
    }

    /* Вилучення з кільцевого буфера */
    db_connection_t* conn = pool->idle_ring[pool->ring_head];
    pool->ring_head = (pool->ring_head + 1) % pool->config.capacity;
    pool->idle_count--;

    uint64_t now = get_time_monotonic_ms();

    /* Перевірка максимального віку (Max Lifetime) */
    if (now - conn->created_at_ms > pool->config.max_lifetime_ms) {
        db_connection_destroy(conn);
        conn = db_connection_create();
    }
    /* Перевірка після тривалого простою */
    else if (now - conn->last_used_at_ms > pool->config.idle_validation_timeout_ms) {
        if (!db_connection_validate(conn)) {
            db_connection_destroy(conn);
            conn = db_connection_create();
        }
    }

    /* Реєстрація в таблиці оренд */
    for (size_t i = 0; i < pool->config.capacity; ++i) {
        if (!pool->lease_table[i].in_use) {
            pool->lease_table[i].conn = conn;
            pool->lease_table[i].owner_thread = pthread_self();
            pool->lease_table[i].borrowed_at_ms = now;
            pool->lease_table[i].in_use = true;
            pool->active_leases++;
            break;
        }
    }

    pthread_mutex_unlock(&pool->lock);
    return conn;
}

/* Повернення з'єднання в пул */
void connection_pool_release(connection_pool_t* pool, db_connection_t* conn) {
    if (!pool || !conn) return;

    pthread_mutex_lock(&pool->lock);

    /* Видалення з реєстру активних оренд */
    for (size_t i = 0; i < pool->config.capacity; ++i) {
        if (pool->lease_table[i].in_use && pool->lease_table[i].conn == conn) {
            pool->lease_table[i].in_use = false;
            pool->lease_table[i].conn = NULL;
            pool->active_leases--;
            break;
        }
    }

    conn->last_used_at_ms = get_time_monotonic_ms();

    /* Повернення в кільцевий буфер */
    pool->idle_ring[pool->ring_tail] = conn;
    pool->ring_tail = (pool->ring_tail + 1) % pool->config.capacity;
    pool->idle_count++;

    pthread_cond_signal(&pool->not_empty_cond);

    if (pool->is_shutdown && pool->active_leases == 0) {
        pthread_cond_broadcast(&pool->drain_cond);
    }

    pthread_mutex_unlock(&pool->lock);
}

/* Плавний дренаж і знищення пулу */
void connection_pool_destroy(connection_pool_t* pool) {
    if (!pool) return;

    pthread_mutex_lock(&pool->lock);
    pool->is_shutdown = true;
    pthread_cond_broadcast(&pool->not_empty_cond);

    /* Очікування повернення всіх активних оренд */
    while (pool->active_leases > 0) {
        pthread_cond_wait(&pool->drain_cond, &pool->lock);
    }
    pthread_mutex_unlock(&pool->lock);

    /* Зупинка вартового */
    pthread_join(pool->watchdog_thread, NULL);

    /* Звільнення сокетів */
    while (pool->idle_count > 0) {
        db_connection_t* conn = pool->idle_ring[pool->ring_head];
        pool->ring_head = (pool->ring_head + 1) % pool->config.capacity;
        pool->idle_count--;
        db_connection_destroy(conn);
    }

    pthread_mutex_destroy(&pool->lock);
    pthread_cond_destroy(&pool->not_empty_cond);
    pthread_cond_destroy(&pool->drain_cond);

    free(pool->idle_ring);
    free(pool->lease_table);
    free(pool);
}
