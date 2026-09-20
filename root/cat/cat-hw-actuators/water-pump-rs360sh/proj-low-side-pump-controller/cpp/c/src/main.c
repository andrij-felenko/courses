#include "water_pump_controller.h"
#include <stdio.h>
#include <time.h>
#include <unistd.h> // Для usleep

// Симуляція апаратного ШІМ
void mock_pwm_set_duty(uint8_t duty) {
    printf("[PWM] Duty cycle set to %d\n", duty);
}

// Отримання мілісекунд
uint32_t mock_get_time_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint32_t)(ts.tv_sec * 1000 + ts.tv_nsec / 1000000);
}

int main(void) {
    water_pump_config_t config = {
        .soft_start_duration_ms = 2000,
        .watchdog_timeout_ms = 5000,
        .min_duty_cycle = 50,
        .max_duty_cycle = 255,
        .pwm_set_duty = mock_pwm_set_duty,
        .get_time_ms = mock_get_time_ms
    };

    water_pump_controller_t pump;
    water_pump_init(&pump, &config);

    printf("Starting pump...\n");
    water_pump_start(&pump);

    uint32_t start_time = mock_get_time_ms();

    while (1) {
        water_pump_update(&pump);

        uint32_t now = mock_get_time_ms();
        uint32_t elapsed = now - start_time;

        // Імітація роботи датчика потоку
        static uint32_t last_simulated_reset = 0;
        if (elapsed - last_simulated_reset >= 1000 && elapsed < 6000) {
            printf("[Sensor] Water flow detected, resetting watchdog.\n");
            water_pump_reset_watchdog(&pump);
            last_simulated_reset = elapsed;
        }

        if (water_pump_is_fault(&pump)) {
            printf("Pump FAULT! Dry run detected.\n");
            break;
        }

        usleep(100 * 1000); // Затримка 100мс
    }

    return 0;
}
