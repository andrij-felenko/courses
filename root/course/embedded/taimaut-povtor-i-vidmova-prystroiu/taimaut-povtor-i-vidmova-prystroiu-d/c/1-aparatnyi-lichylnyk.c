#include <stdint.h>
#include <stdbool.h>

/* Структури та маски Cortex-M DWT/CoreDebug */
#define DWT_CTRL_CYCCNTENA_BIT (1UL << 0)
#define COREDEBUG_DEMCR_TRCENA_BIT (1UL << 24)

/* Ініціалізація апаратного лічильника тактів DWT Cortex-M */
void dwt_timer_init(void) {
    /* Дозволяємо модуль трасування в CoreDebug */
    CoreDebug->DEMCR |= COREDEBUG_DEMCR_TRCENA_BIT;
    /* Скидаємо поточне значення лічильника */
    DWT->CYCCNT = 0;
    /* Вмикаємо підрахунок тактів ядра */
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_BIT;
}

/* Структура контролю дедлайну в мікросекундах */
typedef struct {
    uint32_t start_cycles;
    uint32_t timeout_cycles;
} timeout_dwt_t;

void timeout_dwt_start(timeout_dwt_t *t, uint32_t timeout_us, uint32_t cpu_freq_hz) {
    t->start_cycles = DWT->CYCCNT;
    /* Кількість тактів ядра на вказаний інтервал мікросекунд */
    t->timeout_cycles = timeout_us * (cpu_freq_hz / 1000000UL);
}

bool timeout_dwt_expired(const timeout_dwt_t *t) {
    /* Беззнакова різниця автоматично коректна при переході через 0xFFFFFFFF */
    uint32_t elapsed = DWT->CYCCNT - t->start_cycles;
    return elapsed >= t->timeout_cycles;
}
