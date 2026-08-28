#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>

/* Інтерфейс драйвера вимірювача енергії */
typedef struct {
    float voltage_rms;
    float current_rms;
    float active_power;
    float apparent_power;
    float power_factor;
    double energy_kwh;
} socket_telemetry_t;

/* Обробка оновлених метрик у головному циклі пристрою */
void handle_socket_telemetry(const socket_telemetry_t *data) {
    if (!data) return;

    /* Захист від перевантаження за струмом (16 А) */
    if (data->current_rms > 16.5f) {
        // Екстрене вимкнення силового реле
        // relay_set_state(false);
    }

    /* Захист від аварійної напруги в мережі */
    if (data->voltage_rms > 260.0f || data->voltage_rms < 175.0f) {
        // Сигналізація аварії мережі
    }
}
