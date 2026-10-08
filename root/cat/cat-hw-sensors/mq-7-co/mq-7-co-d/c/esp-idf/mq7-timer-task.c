// Асинхронний драйвер двофазного нагріву MQ-7 (C / ESP-IDF)
#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "driver/ledc.h"

#define HEATER_GPIO          GPIO_NUM_18
#define LEDC_CHANNEL         LEDC_CHANNEL_0
#define LEDC_TIMER           LEDC_TIMER_0
#define LEDC_MODE            LEDC_LOW_SPEED_MODE

void mq7_timer_task(void *pvParameters) {
    ledc_timer_config_t ledc_timer = {
        .speed_mode       = LEDC_MODE,
        .timer_num        = LEDC_TIMER,
        .duty_resolution  = LEDC_TIMER_13_BIT,
        .freq_hz          = 5000,
        .clk_cfg          = LEDC_AUTO_CLK
    };
    ledc_timer_config(&ledc_timer);

    ledc_channel_config_t ledc_channel = {
        .speed_mode     = LEDC_MODE,
        .channel        = LEDC_CHANNEL,
        .timer_sel      = LEDC_TIMER,
        .intr_type      = LEDC_INTR_DISABLE,
        .gpio_num       = HEATER_GPIO,
        .duty           = 8191, // 100% duty cycle -> 5.0V
        .hpoint         = 0
    };
    ledc_channel_config(&ledc_channel);

    while (1) {
        // Фаза 1: 5.0 V протягом 60 секунд (регенерація)
        ledc_set_duty(LEDC_MODE, LEDC_CHANNEL, 8191);
        ledc_update_duty(LEDC_MODE, LEDC_CHANNEL);
        vTaskDelay(pdMS_TO_TICKS(60000));

        // Фаза 2: 1.4 V (28% duty = 2293) протягом 90 секунд (вимірювання)
        ledc_set_duty(LEDC_MODE, LEDC_CHANNEL, 2293);
        ledc_update_duty(LEDC_MODE, LEDC_CHANNEL);

        // Пауза 85 секунд до моменту вимірювання
        vTaskDelay(pdMS_TO_TICKS(85000));

        // Зчитування АЦП наприкінці фази низького нагріву

        // Дочекатися завершення 90-секундного інтервалу (ще 5 секунд)
        vTaskDelay(pdMS_TO_TICKS(5000));
    }
}
