#include "driver/ledc.h"

// --- параметри ключа ---
static const int      GATE_PIN   = 25;         // нога → вхід драйвера затвора
static const uint32_t PWM_FREQ   = 20000;      // 20 кГц: тихо для вуха, помірна комутація
static const ledc_timer_bit_t PWM_RES = LEDC_TIMER_11_BIT;  // 2^11 = 2048 кроків
static const uint32_t DUTY_MAX   = (1u << 11) - 1;          // 2047

void gate_pwm_init(void) {
    ledc_timer_config_t t = {
        .speed_mode      = LEDC_LOW_SPEED_MODE,
        .duty_resolution = PWM_RES,
        .timer_num       = LEDC_TIMER_0,
        .freq_hz         = PWM_FREQ,
        .clk_cfg         = LEDC_AUTO_CLK,
    };
    ledc_timer_config(&t);

    ledc_channel_config_t c = {
        .gpio_num   = GATE_PIN,
        .speed_mode = LEDC_LOW_SPEED_MODE,
        .channel    = LEDC_CHANNEL_0,
        .timer_sel  = LEDC_TIMER_0,
        .duty       = 0,          // старт із закритого ключа — важливо!
        .hpoint     = 0,
    };
    ledc_channel_config(&c);
}

// встановити шпаруватість 0..100 % (частку часу ключ відкритий)
void gate_set_duty_percent(float pct) {
    if (pct < 0)   pct = 0;
    if (pct > 100) pct = 100;
    uint32_t duty = (uint32_t)(pct / 100.0f * DUTY_MAX);
    ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, duty);
    ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0);
}
