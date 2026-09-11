#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "esp_adc/adc_oneshot.h"
#include "driver/ledc.h"

static const char *TAG = "SERVO_GUARD";

#define SERVO_LEDC_MODE        LEDC_LOW_SPEED_MODE
#define SERVO_LEDC_CHANNEL     LEDC_CHANNEL_0
#define SHUNT_RESISTANCE_OHM   0.22f
#define SHUNT_AMP_GAIN         1.0f
#define STALL_CURRENT_MA       550.0f
#define STALL_MAX_TIME_MS      150

typedef struct {
    adc_oneshot_unit_handle_t adc_handle;
    adc_channel_t adc_channel;
    uint32_t stall_timer_ms;
    bool is_tripped;
} servo_stall_guard_t;

static void servo_emergency_stop(servo_stall_guard_t *guard) {
    ledc_stop(SERVO_LEDC_MODE, SERVO_LEDC_CHANNEL, 0); // Рівень 0 знеструмлює мотор
    guard->is_tripped = true;
    ESP_LOGE(TAG, "АВАРІЯ: Зафіксовано заклинювання вала! ШІМ знеструмлено.");
}

// Завдання опитування струмового шунта (період опитування 10 мс)
void servo_stall_monitor_task(void *pvParameters) {
    servo_stall_guard_t *guard = (servo_stall_guard_t *)pvParameters;
    const TickType_t delay_ticks = pdMS_TO_TICKS(10);

    while (1) {
        if (!guard->is_tripped) {
            int raw_val = 0;
            ESP_ERROR_CHECK(adc_oneshot_read(guard->adc_handle, guard->adc_channel, &raw_val));

            // Перерахунок АЦП (12 біт, діапазон 0-3300 мВ)
            float v_shunt_mv = (raw_val * 3300.0f) / 4095.0f;
            float current_ma = (v_shunt_mv / (SHUNT_AMP_GAIN * SHUNT_RESISTANCE_OHM));

            if (current_ma >= STALL_CURRENT_MA) {
                guard->stall_timer_ms += 10;
                if (guard->stall_timer_ms >= STALL_MAX_TIME_MS) {
                    servo_emergency_stop(guard);
                }
            } else {
                guard->stall_timer_ms = 0; // Скидання після пускового сплеску
            }
        }
        vTaskDelay(delay_ticks);
    }
}
