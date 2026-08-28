#include <stdint.h>
#include <stdbool.h>

#define MAX_CURRENT_AMPS         45.0f
#define DESYNC_RPM_DROP_RATIO    0.40f
#define ZCP_TIMEOUT_MICROS       1500

typedef struct {
    float filtered_current;
    uint32_t expected_erpm;
    uint32_t measured_erpm;
    uint32_t last_commutation_us;
    uint8_t desync_counter;
    bool motor_stalled;
} esc_health_monitor_t;

void esc_monitor_init(esc_health_monitor_t *mon) {
    mon->filtered_current = 0.0f;
    mon->expected_erpm = 0;
    mon->measured_erpm = 0;
    mon->last_commutation_us = 0;
    mon->desync_counter = 0;
    mon->motor_stalled = false;
}

bool esc_check_commutation_health(esc_health_monitor_t *mon,
                                  float raw_current,
                                  uint32_t current_erpm,
                                  uint32_t now_us) {
    /* 1. Фільтрація струму (експоненційне ковзне середнє) */
    mon->filtered_current = 0.85f * mon->filtered_current + 0.15f * raw_current;

    /* 2. Перевірка таймауту детекції нульової проти-ЕРС */
    if ((now_us - mon->last_commutation_us) > ZCP_TIMEOUT_MICROS && mon->expected_erpm > 3000) {
        mon->desync_counter++;
    } else if (mon->desync_counter > 0) {
        mon->desync_counter--;
    }

    /* 3. Детекція раптового падіння обертів під великим струмом */
    if (mon->filtered_current > MAX_CURRENT_AMPS &&
        current_erpm < (uint32_t)(mon->expected_erpm * DESYNC_RPM_DROP_RATIO)) {
        mon->desync_counter += 3;
    }

    /* 4. Захисне вимкнення при накопиченні помилок */
    if (mon->desync_counter >= 6) {
        mon->motor_stalled = true;
        return false; /* Зрив синхронізації виявлено: скинути шпаруватість у 0! */
    }

    mon->measured_erpm = current_erpm;
    mon->last_commutation_us = now_us;
    return true;
}
