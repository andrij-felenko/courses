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

#define MAX_POOL_CAPACITY 64

/* Структура дескриптора з'єднання з базою */
typedef struct {
    int socket_fd;
    uint64_t created_at_ms;
    uint64_t last_used_at_ms;
    bool is_valid;
} db_conn_t;

/* Структура потокобезпечного пулу */
typedef struct {
    db_conn_t* connections[MAX_POOL_CAPACITY];
    size_t top;
    size_t capacity;
    uint64_t acquire_timeout_ms;
    uint64_t idle_validation_ms;
    
    pthread_mutex_t lock;
    pthread_cond_t cond_available;
    bool is_closed;
} db_pool_t;

/* Отримання поточного монотонного часу в мілісекундах */
static uint64_t get_time_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000ULL + (uint64_t)ts.tv_nsec / 1000000ULL;
}

/* Перевірка життєздатності з'єднання */
static bool db_conn_ping(db_conn_t* conn) {
    if (!conn || conn->socket_fd < 0) return false;
    /* Імітація швидкого пінгу сокета */
    return true;
}

/* Ініціалізація пулу */
int db_pool_init(db_pool_t* pool, size_t capacity, uint64_t timeout_ms, uint64_t idle_val_ms) {
    if (!pool || capacity == 0 || capacity > MAX_POOL_CAPACITY) return -1;
    
    memset(pool, 0, sizeof(*pool));
    pool->capacity = capacity;
    pool->acquire_timeout_ms = timeout_ms;
    pool->idle_validation_ms = idle_val_ms;
    
    if (pthread_mutex_init(&pool->lock, NULL) != 0) return -1;
    if (pthread_cond_init(&pool->cond_available, NULL) != 0) {
        pthread_mutex_destroy(&pool->lock);
        return -1;
    }
    
    /* Попереднє створення (прогрів) сокетів */
    uint64_t now = get_time_ms();
    for (size_t i = 0; i < capacity; i++) {
        db_conn_t* conn = (db_conn_t*)malloc(sizeof(db_conn_t));
        if (!conn) return -1;
        conn->socket_fd = 100 + (int)i; /* Імітація сокета */
        conn->created_at_ms = now;
        conn->last_used_at_ms = now;
        conn->is_valid = true;
        
        pool->connections[pool->top++] = conn;
    }
    
    return 0;
}

/* Оренда з'єднання з дедлайном */
db_conn_t* db_pool_acquire(db_pool_t* pool) {
    if (!pool) return NULL;
    
    struct timespec abs_deadline;
    clock_gettime(CLOCK_REALTIME, &abs_deadline);
    
    uint64_t add_ns = (uint64_t)abs_deadline.tv_nsec + (pool->acquire_timeout_ms % 1000ULL) * 1000000ULL;
    abs_deadline.tv_sec += (time_t)(pool->acquire_timeout_ms / 1000ULL) + (time_t)(add_ns / 1000000000ULL);
    abs_deadline.tv_nsec = (long)(add_ns % 1000000000ULL);
    
    pthread_mutex_lock(&pool->lock);
    
    while (pool->top == 0 && !pool->is_closed) {
        int rc = pthread_cond_timedwait(&pool->cond_available, &pool->lock, &abs_deadline);
        if (rc == ETIMEDOUT) {
            pthread_mutex_unlock(&pool->lock);
            return NULL; /* Вичерпано бюджет очікування */
        }
    }
    
    if (pool->is_closed) {
        pthread_mutex_unlock(&pool->lock);
        return NULL;
    }
    
    /* Вилучення сокета зі стека LIFO */
    db_conn_t* conn = pool->connections[--pool->top];
    pthread_mutex_unlock(&pool->lock);
    
    /* Перевірка потреби у валідації за віком простою */
    uint64_t now = get_time_ms();
    if (now - conn->last_used_at_ms > pool->idle_validation_ms) {
        if (!db_conn_ping(conn)) {
            /* Перепідключення у разі збою */
            conn->socket_fd = 200 + (int)(now % 1000);
            conn->created_at_ms = now;
        }
    }
    
    return conn;
}

/* Повернення сокета та сповіщення очікувача */
void db_pool_release(db_pool_t* pool, db_conn_t* conn) {
    if (!pool || !conn) return;
    
    conn->last_used_at_ms = get_time_ms();
    
    pthread_mutex_lock(&pool->lock);
    if (pool->top < pool->capacity) {
        pool->connections[pool->top++] = conn;
        pthread_cond_signal(&pool->cond_available);
    } else {
        /* Переповнення буфера: аварійне закриття сокета */
        close(conn->socket_fd);
        free(conn);
    }
    pthread_mutex_unlock(&pool->lock);
}

/* Знищення пулу */
void db_pool_destroy(db_pool_t* pool) {
    if (!pool) return;
    
    pthread_mutex_lock(&pool->lock);
    pool->is_closed = true;
    pthread_cond_broadcast(&pool->cond_available);
    
    for (size_t i = 0; i < pool->top; i++) {
        if (pool->connections[i]) {
            free(pool->connections[i]);
        }
    }
    pool->top = 0;
    pthread_mutex_unlock(&pool->lock);
    
    pthread_mutex_destroy(&pool->lock);
    pthread_cond_destroy(&pool->cond_available);
}
