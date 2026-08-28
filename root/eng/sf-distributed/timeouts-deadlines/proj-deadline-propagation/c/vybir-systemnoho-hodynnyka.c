#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
#include <poll.h>
#include <pthread.h>
#include <sys/socket.h>
#include <netinet/in.h>

/* Отримання поточного монотонного часу в мілісекундах */
static inline int64_t monotonic_now_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (int64_t)ts.tv_sec * 1000 + (int64_t)(ts.tv_nsec / 1000000);
}

/* Структура контексту дедлайну */
typedef struct {
    int64_t deadline_ms;       /* Абсолютна часова мітка на монотонному годиннику */
    int64_t safety_margin_ms;  /* Запас на серіалізацію та зворотну передачу */
    bool is_cancelled;         /* Прапорець явного скасування */
} deadline_context_t;

/* Створення кореневого контексту з тривалістю в мілісекундах */
deadline_context_t context_with_timeout(int64_t timeout_ms, int64_t margin_ms) {
    deadline_context_t ctx;
    ctx.deadline_ms = monotonic_now_ms() + timeout_ms;
    ctx.safety_margin_ms = margin_ms;
    ctx.is_cancelled = false;
    return ctx;
}

/* Отримання залишку доступного часу в мілісекундах */
int64_t context_remaining_ms(const deadline_context_t *ctx) {
    if (ctx->is_cancelled) {
        return 0;
    }
    int64_t now = monotonic_now_ms();
    if (now >= ctx->deadline_ms) {
        return 0;
    }
    return ctx->deadline_ms - now;
}

/* Перевірка, чи не вичерпано дедлайн */
bool context_is_expired(const deadline_context_t *ctx) {
    return context_remaining_ms(ctx) <= 0;
}

/* Ручне скасування контексту */
void context_cancel(deadline_context_t *ctx) {
    ctx->is_cancelled = true;
}
