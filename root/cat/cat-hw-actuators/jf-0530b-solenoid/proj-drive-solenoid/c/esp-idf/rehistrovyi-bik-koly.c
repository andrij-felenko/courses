// ESP-IDF: той самий LEDC, але частота й роздільність задаються явно
#include "driver/ledc.h"
#define SOL_PIN  GPIO_NUM_5

void solenoid_setup(void) {
    ledc_timer_config_t t = {
        .speed_mode      = LEDC_LOW_SPEED_MODE,
        .timer_num       = LEDC_TIMER_0,
        .duty_resolution = LEDC_TIMER_8_BIT,   // шпаруватість 0..255
        .freq_hz         = 25000,              // 25 кГц — поза чутним діапазоном
        .clk_cfg         = LEDC_AUTO_CLK,
    };
    ESP_ERROR_CHECK(ledc_timer_config(&t));
    ledc_channel_config_t c = {
        .gpio_num   = SOL_PIN,
        .speed_mode = LEDC_LOW_SPEED_MODE,
        .channel    = LEDC_CHANNEL_0,
        .timer_sel  = LEDC_TIMER_0,
        .duty       = 0,
        .hpoint     = 0,
    };
    ESP_ERROR_CHECK(ledc_channel_config(&c));
}

static void sol_duty(uint32_t d) {
    ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, d);
    ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0);
}

void solenoid_peak(void) { sol_duty(255); }  // повний струм на втягування
void solenoid_hold(void) { sol_duty(90);  }  // ≈35% — тихе утримання
void solenoid_off (void) { sol_duty(0);   }  // відпустити
