#include <stdint.h>
#include <stdbool.h>

extern uint32_t platform_get_millis(void);

typedef enum {
    CB_STATE_CLOSED = 0,    /* Штатна робота */
    CB_STATE_OPEN,          /* Відмова, запити блокуються */
    CB_STATE_HALF_OPEN      /* Пробна перевірка */
} circuit_state_t;

typedef struct {
    circuit_state_t state;
    uint8_t  failure_count;
    uint8_t  failure_threshold;   /* Поріг відмов для розриву (наприклад, 5) */
    uint32_t state_change_time_ms;
    uint32_t cooldown_period_ms;  /* Час ізоляції чипа (наприклад, 5000 мс) */
    uint32_t total_errors_logged; /* Загальний лічильник для діагностики */
} circuit_breaker_t;

void cb_init(circuit_breaker_t *cb, uint8_t threshold, uint32_t cooldown_ms) {
    cb->state = CB_STATE_CLOSED;
    cb->failure_count = 0;
    cb->failure_threshold = threshold;
    cb->state_change_time_ms = 0;
    cb->cooldown_period_ms = cooldown_ms;
    cb->total_errors_logged = 0;
}

/* Перевірка, чи дозволено виконувати фізичну транзакцію */
bool cb_allow_transaction(circuit_breaker_t *cb) {
    uint32_t now = platform_get_millis();

    switch (cb->state) {
        case CB_STATE_CLOSED:
            return true;

        case CB_STATE_OPEN:
            /* Перевіряємо, чи минув час охолодження */
            if ((now - cb->state_change_time_ms) >= cb->cooldown_period_ms) {
                cb->state = CB_STATE_HALF_OPEN;
                return true; /* Дозволяємо одну пробну транзакцію */
            }
            return false; /* Швидка відмова: не навантажуємо шину */

        case CB_STATE_HALF_OPEN:
            /* Пробна транзакція вже в процесі */
            return false;

        default:
            return false;
    }
}

/* Фіксація успішного виконання транзакції */
void cb_report_success(circuit_breaker_t *cb) {
    cb->failure_count = 0;
    if (cb->state != CB_STATE_CLOSED) {
        cb->state = CB_STATE_CLOSED;
        cb->state_change_time_ms = platform_get_millis();
    }
}

/* Фіксація помилки виконання транзакції */
void cb_report_failure(circuit_breaker_t *cb) {
    cb->total_errors_logged++;
    uint32_t now = platform_get_millis();

    if (cb->state == CB_STATE_HALF_OPEN) {
        /* Проба провалилася: миттєво повертаємось в OPEN */
        cb->state = CB_STATE_OPEN;
        cb->state_change_time_ms = now;
        /* Можна подвоїти період очікування: cb->cooldown_period_ms *= 2; */
    } else if (cb->state == CB_STATE_CLOSED) {
        cb->failure_count++;
        if (cb->failure_count >= cb->failure_threshold) {
            cb->state = CB_STATE_OPEN;
            cb->state_change_time_ms = now;
        }
    }
}
