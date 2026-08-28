// Те саме на чистому ESP-IDF 5.x: таймер LEDC задає частоту, канал — вивід
#include "driver/ledc.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define PWM_GPIO   25                     // будь-який GPIO, здатний на вихід LEDC
#define PWM_FREQ   25000                  // 25 кГц — вище за поріг слуху
#define PWM_BITS   LEDC_TIMER_8_BIT       // 8 біт розрядності → duty 0…255
#define DUTY_MAX   255

static void fan_set_speed(uint8_t percent) {      // 0…100 % → duty
    if (percent > 100) percent = 100;
    uint32_t duty = (uint32_t)percent * DUTY_MAX / 100;
    ESP_ERROR_CHECK(ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, duty));
    ESP_ERROR_CHECK(ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0));
}

void app_main(void) {
    ledc_timer_config_t timer = {                 // крок 1: частота й розрядність
        .speed_mode      = LEDC_LOW_SPEED_MODE,
        .duty_resolution = PWM_BITS,
        .timer_num       = LEDC_TIMER_0,
        .freq_hz         = PWM_FREQ,
        .clk_cfg         = LEDC_AUTO_CLK,         // джерело такту вибере драйвер
    };
    ESP_ERROR_CHECK(ledc_timer_config(&timer));

    ledc_channel_config_t chan = {                // крок 2: прив'язка до виводу
        .gpio_num   = PWM_GPIO,
        .speed_mode = LEDC_LOW_SPEED_MODE,
        .channel    = LEDC_CHANNEL_0,
        .intr_type  = LEDC_INTR_DISABLE,
        .timer_sel  = LEDC_TIMER_0,
        .duty       = 0,                          // старт: вентилятор стоїть
        .hpoint     = 0,
    };
    ESP_ERROR_CHECK(ledc_channel_config(&chan));

    while (1) {   // повільний «вдих-видих» швидкістю — щоб НЕ почути роботу
        for (int p = 20; p <= 100; p += 5) { fan_set_speed(p); vTaskDelay(pdMS_TO_TICKS(200)); }
        for (int p = 100; p >= 20; p -= 5) { fan_set_speed(p); vTaskDelay(pdMS_TO_TICKS(200)); }
    }
}
