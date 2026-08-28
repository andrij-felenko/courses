#include <stdint.h>
#include <stdbool.h>

extern uint32_t get_system_ticks_ms(void);
extern void sensor_read_start(void);
extern bool sensor_is_ready(void);
extern void sensor_get_data(float *out_temp, float *out_press);
extern void display_update(float temp, float press);
extern void watchdog_reload(void);

typedef struct {
    uint32_t last_sensor_time;
    uint32_t last_display_time;
    float current_temperature;
    float current_pressure;
} app_context_t;

void superloop_run(void) {
    app_context_t ctx = {0};
    sensor_read_start();

    while (1) {
        uint32_t now = get_system_ticks_ms();

        // 1. Неблокуюче опитування сенсора кожні 100 мс
        if ((now - ctx.last_sensor_time) >= 100) {
            if (sensor_is_ready()) {
                sensor_get_data(&ctx.current_temperature, &ctx.current_pressure);
                ctx.last_sensor_time = now;
                sensor_read_start(); // запуск наступного вимірювання
            }
        }

        // 2. Оновлення екрана кожні 500 мс
        if ((now - ctx.last_display_time) >= 500) {
            display_update(ctx.current_temperature, ctx.current_pressure);
            ctx.last_display_time = now;
        }

        // 3. Скидання сторожового таймера
        watchdog_reload();
    }
}
