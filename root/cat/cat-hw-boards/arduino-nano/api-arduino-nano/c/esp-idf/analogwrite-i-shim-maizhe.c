#include "driver/ledc.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define PIN_LED 2   // будь-який GPIO: ШІМ розводить матриця, не жорсткі виводи

static void set_duty(int d) {
    ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, d);
    ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0);
}

void app_main(void) {
    const ledc_timer_config_t tm = {
        .speed_mode      = LEDC_LOW_SPEED_MODE,
        .timer_num       = LEDC_TIMER_0,
        .duty_resolution = LEDC_TIMER_8_BIT,   // 8 бітів: duty 0..255, як у Arduino
        .freq_hz         = 5000,               // частоту обираємо самі
        .clk_cfg         = LEDC_AUTO_CLK,
    };
    ESP_ERROR_CHECK(ledc_timer_config(&tm));

    const ledc_channel_config_t ch = {
        .gpio_num = PIN_LED, .speed_mode = LEDC_LOW_SPEED_MODE,
        .channel  = LEDC_CHANNEL_0, .timer_sel = LEDC_TIMER_0,
        .duty = 0, .hpoint = 0,
    };
    ESP_ERROR_CHECK(ledc_channel_config(&ch));

    while (1) {
        // плавне «дихання»: яскравість вгору й вниз
        for (int d = 0;   d <= 255; d++) { set_duty(d); vTaskDelay(pdMS_TO_TICKS(5)); }
        for (int d = 255; d >= 0;   d--) { set_duty(d); vTaskDelay(pdMS_TO_TICKS(5)); }
    }
}
