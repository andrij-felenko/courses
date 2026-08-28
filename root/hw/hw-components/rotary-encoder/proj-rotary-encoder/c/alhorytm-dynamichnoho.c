#include <stdint.h>

#define ACCEL_FAST_THRESHOLD_MS  20
#define ACCEL_MED_THRESHOLD_MS   50
#define ACCEL_SLOW_THRESHOLD_MS  100

int32_t calculate_accelerated_step(uint32_t delta_time_ms, int32_t direction) {
    int32_t multiplier = 1;

    if (delta_time_ms < ACCEL_FAST_THRESHOLD_MS) {
        multiplier = 20;  /* Дуже швидке обертання: стрибок на 20 одиниць */
    } else if (delta_time_ms < ACCEL_MED_THRESHOLD_MS) {
        multiplier = 5;   /* Середня швидкість: крок на 5 одиниць */
    } else if (delta_time_ms < ACCEL_SLOW_THRESHOLD_MS) {
        multiplier = 2;   /* Помірне обертання */
    } else {
        multiplier = 1;   /* Повільне точне позиціонування */
    }

    return direction * multiplier;
}
