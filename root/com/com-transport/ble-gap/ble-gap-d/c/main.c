#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint16_t interval_min;    /* Крок 1.25 мс (наприклад, 6 = 7.5 мс, 800 = 1000 мс) */
    uint16_t interval_max;    /* Крок 1.25 мс */
    uint16_t latency;         /* Кількість подій (0 .. 499) */
    uint16_t timeout;         /* Крок 10 мс (наприклад, 100 = 1000 мс, 600 = 6000 мс) */
} ble_gap_conn_params_t;

/* Перевірка валідності параметрів згідно зі специфікацією Bluetooth Core v5.x */
bool ble_gap_validate_conn_params(const ble_gap_conn_params_t *p) {
    if (!p) return false;

    /* Межі інтервалу: від 7.5 мс (0x0006) до 4000 мс (0x0C80) */
    if (p->interval_min < 6 || p->interval_min > 3200) return false;
    if (p->interval_max < p->interval_min || p->interval_max > 3200) return false;

    /* Межі затримки Slave Latency */
    if (p->latency > 499) return false;

    /* Межі таймауту нагляду: від 100 мс (0x000A) до 32000 мс (0x0C80) */
    if (p->timeout < 10 || p->timeout > 3200) return false;

    /* Математична перевірка узгодженості:
       Timeout (мс) > (1 + Latency) * 2 * Max_Interval (мс)
       Враховуємо одиниці: Timeout * 10 мс > (1 + Latency) * 2 * (Max_Interval * 1.25 мс)
       Спрощення: Timeout * 10 > (1 + Latency) * 2.5 * Max_Interval
       У цілих числах: Timeout * 20 > (1 + Latency) * 5 * Max_Interval -> Timeout * 4 > (1 + Latency) * Max_Interval */
    uint32_t max_effective_interval_units = (uint32_t)(1 + p->latency) * p->interval_max;
    uint32_t timeout_scaled = (uint32_t)p->timeout * 4;

    return (timeout_scaled > max_effective_interval_units);
}
