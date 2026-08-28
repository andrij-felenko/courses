#include "driver/ledc.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define LAMP_PIN GPIO_NUM_9        // вивід, заведений на канал LEDC

static void lamp_set(int duty) {   // 0 = темно, 255 = повний
    ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, duty);
    ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0);
}

void lamp_task(void *arg) {
    ledc_timer_config_t tcfg = {
        .speed_mode      = LEDC_LOW_SPEED_MODE,
        .timer_num       = LEDC_TIMER_0,
        .duty_resolution = LEDC_TIMER_8_BIT,   // шпаруватість 0..255
        .freq_hz         = 1000,
        .clk_cfg         = LEDC_AUTO_CLK,
    };
    ESP_ERROR_CHECK(ledc_timer_config(&tcfg));

    ledc_channel_config_t ccfg = {
        .gpio_num   = LAMP_PIN,
        .speed_mode = LEDC_LOW_SPEED_MODE,
        .channel    = LEDC_CHANNEL_0,
        .timer_sel  = LEDC_TIMER_0,
        .duty       = 0,
        .hpoint     = 0,
    };
    ESP_ERROR_CHECK(ledc_channel_config(&ccfg));

    for (;;) {
        for (int d = 0; d <= 255; d++) { lamp_set(d); vTaskDelay(pdMS_TO_TICKS(8)); }  // розгоряння
        for (int d = 255; d >= 0; d--) { lamp_set(d); vTaskDelay(pdMS_TO_TICKS(8)); }  // згасання
    }
}
