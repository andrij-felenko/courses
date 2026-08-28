/* Приклад організації неблокуючого головного циклу прошивки на C */
#include <stdint.h>
#include <stdbool.h>

extern uint32_t get_system_micros(void);
extern void fast_loop_gyro_and_motors_1khz(void);
extern void medium_loop_attitude_250hz(void);
extern void slow_loop_telemetry_10hz(void);

void main_superloop(void) {
    uint32_t last_1khz_time = get_system_micros();
    uint32_t last_250hz_time = last_1khz_time;
    uint32_t last_10hz_time = last_1khz_time;

    while (1) {
        uint32_t current_time = get_system_micros();

        /* Швидкий контур: 1 кГц (кожні 1000 мкс) */
        if ((current_time - last_1khz_time) >= 1000) {
            last_1khz_time += 1000;
            fast_loop_gyro_and_motors_1khz();
        }

        /* Середній контур: 250 Гц (кожні 4000 мкс) */
        if ((current_time - last_250hz_time) >= 4000) {
            last_250hz_time += 4000;
            medium_loop_attitude_250hz();
        }

        /* Повільний контур: 10 Гц (кожні 100000 мкс) */
        if ((current_time - last_10hz_time) >= 100000) {
            last_10hz_time += 100000;
            slow_loop_telemetry_10hz();
        }
    }
}
