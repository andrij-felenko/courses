#include <stdint.h>
#include <stdbool.h>

/* Отримання глобального монотонного часу системи у мілісекундах */
extern uint32_t platform_get_millis(void);

typedef struct {
    uint32_t start_ms;
    uint32_t timeout_ms;
} timeout_ms_t;

void timeout_ms_start(timeout_ms_t *t, uint32_t timeout_ms) {
    t->start_ms = platform_get_millis();
    t->timeout_ms = timeout_ms;
}

bool timeout_ms_expired(const timeout_ms_t *t) {
    uint32_t elapsed = platform_get_millis() - t->start_ms;
    return elapsed >= t->timeout_ms;
}
