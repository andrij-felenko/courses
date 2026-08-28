#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdatomic.h>
#include <time.h>
#include <poll.h>
#include <unistd.h>
#include <errno.h>

/* =========================================================================
 * 1. Клієнтський рівень: Регулятор бюджету повторних спроб (Retry Budget)
 * ========================================================================= */

typedef struct {
    atomic_int_fast64_t total_tokens;    /* Баланс доступних токенів */
    atomic_int_fast64_t max_tokens;      /* Максимальна місткість кошика */
    double retry_fraction;               /* Дозволена частка повторів (0.1 = 10%) */
} retry_budget_t;

void retry_budget_init(retry_budget_t *b, int64_t max_capacity, double fraction) {
    atomic_init(&b->total_tokens, max_capacity);
    atomic_init(&b->max_tokens, max_capacity);
    b->retry_fraction = fraction;
}

/* Викликається перед кожним звичайним первинним запитом */
void retry_budget_record_success(retry_budget_t *b) {
    int64_t tokens_to_add = (int64_t)(100.0 * b->retry_fraction);
    int64_t cur = atomic_load_explicit(&b->total_tokens, memory_order_relaxed);
    int64_t max_cap = atomic_load_explicit(&b->max_tokens, memory_order_relaxed);
    
    while (cur < max_cap) {
        int64_t next = (cur + tokens_to_add > max_cap) ? max_cap : cur + tokens_to_add;
        if (atomic_compare_exchange_weak_explicit(&b->total_tokens, &cur, next,
                                                 memory_order_release,
                                                 memory_order_relaxed)) {
            break;
        }
    }
}

/* Перевіряє, чи дозволено клієнту виконати повторний запит */
bool retry_budget_acquire(retry_budget_t *b) {
    const int64_t retry_cost = 100;
    int64_t cur = atomic_load_explicit(&b->total_tokens, memory_order_relaxed);
    
    while (cur >= retry_cost) {
        if (atomic_compare_exchange_weak_explicit(&b->total_tokens, &cur, cur - retry_cost,
                                                 memory_order_acq_rel,
                                                 memory_order_relaxed)) {
            return true; /* Дозвіл надано: списано вартість одного повтору */
        }
    }
    return false; /* Відмовлено: ліміт повторів вичерпано, захист від шторму */
}

/* =========================================================================
 * 2. Серверний рівень: Контролер дедлайнів та перевірки активності клієнта
 * ========================================================================= */

typedef struct {
    int client_socket_fd;       /* Файловий дескриптор сокета клієнта */
    uint64_t deadline_epoch_ms; /* Абсолютний дедлайн у мілісекундах */
    uint64_t min_exec_ms;       /* Мінімальний час, необхідний для обробки */
} request_guard_t;

/* Отримання поточного монотонного часу в мілісекундах */
static inline uint64_t get_monotonic_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000ULL + (uint64_t)ts.tv_nsec / 1000000ULL;
}

void request_guard_init(request_guard_t *g, int fd, uint64_t timeout_ms, uint64_t min_exec_ms) {
    g->client_socket_fd = fd;
    g->deadline_epoch_ms = get_monotonic_ms() + timeout_ms;
    g->min_exec_ms = min_exec_ms;
}

/* Перевірка 1: Чи встигне сервер виконати операцію до дедлайну */
bool request_guard_is_deadline_viable(const request_guard_t *g) {
    uint64_t now = get_monotonic_ms();
    if (now >= g->deadline_epoch_ms) {
        return false; /* Дедлайн уже минув */
    }
    uint64_t remaining = g->deadline_epoch_ms - now;
    return (remaining >= g->min_exec_ms);
}

/* Перевірка 2: Чи не розірвав клієнт TCP-з'єднання під час очікування */
bool request_guard_is_client_alive(const request_guard_t *g) {
    if (g->client_socket_fd < 0) {
        return false;
    }
    struct pollfd pfd;
    pfd.fd = g->client_socket_fd;
    pfd.events = POLLIN | POLLHUP | POLLERR;
    pfd.revents = 0;

    int res = poll(&pfd, 1, 0); /* Миттєвий опитування без блокування */
    if (res < 0) {
        return false;
    }
    if (res > 0) {
        /* Якщо на сокеті виявлено закриття каналу або помилку */
        if (pfd.revents & (POLLHUP | POLLERR | POLLNVAL)) {
            return false;
        }
        /* Якщо сокет сигналізує POLLIN, перевіримо чи це не EOF від клієнта */
        char peek_buf;
        ssize_t bytes = recv(g->client_socket_fd, &peek_buf, 1, MSG_PEEK | MSG_DONTWAIT);
        if (bytes == 0) {
            return false; /* Клієнт надіслав FIN-пакет (сокет закрито) */
        }
    }
    return true;
}

/* =========================================================================
 * 3. Серверний воркер з захистом від виконання марної роботи
 * ========================================================================= */

typedef enum {
    EXEC_SUCCESS = 0,
    EXEC_SHED_DEADLINE = 1,
    EXEC_SHED_CLIENT_ABORT = 2
} exec_status_t;

exec_status_t server_execute_work(request_guard_t *guard) {
    /* Етап 1: Перевірка залишкового бюджету часу перед стартом */
    if (!request_guard_is_deadline_viable(guard)) {
        return EXEC_SHED_DEADLINE; /* Миттєво відхиляємо, не витрачаючи CPU */
    }

    /* Етап 2: Перевірка сокета перед початком важкого звернення до сховища */
    if (!request_guard_is_client_alive(guard)) {
        return EXEC_SHED_CLIENT_ABORT; /* Клієнт уже відключився, робота марна */
    }

    /* Етап 3: Виконання корисної роботи (імітація звернення до БД) */
    usleep(20000); /* 20 мілісекунд корисної обробки */

    /* Етап 4: Повторна перевірка сокета перед формуванням важкої відповіді */
    if (!request_guard_is_client_alive(guard)) {
        return EXEC_SHED_CLIENT_ABORT;
    }

    return EXEC_SUCCESS;
}
