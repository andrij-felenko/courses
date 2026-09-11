#include "driver/ledc.h"

#define BLK_PWM_PIN       4
#define BLK_PWM_FREQ_HZ   20000             // 20 кГц — усуває стробоскопічний ефект і свист MLCC
#define BLK_DUTY_RES      LEDC_TIMER_10_BIT // Роздільність 10 біт (діапазон 0..1023)

// Налаштування апаратного ШІМ LEDC для виводу затвора MOSFET
void st7789_backlight_init(void)
{
    ledc_timer_config_t timer_conf = {
        .speed_mode       = LEDC_LOW_SPEED_MODE,
        .timer_num        = LEDC_TIMER_0,
        .duty_resolution  = BLK_DUTY_RES,
        .freq_hz          = BLK_PWM_FREQ_HZ,
        .clk_cfg          = LEDC_AUTO_CLK
    };
    ledc_timer_config(&timer_conf);

    ledc_channel_config_t channel_conf = {
        .speed_mode     = LEDC_LOW_SPEED_MODE,
        .channel        = LEDC_CHANNEL_0,
        .timer_sel      = LEDC_TIMER_0,
        .intr_type      = LEDC_INTR_DISABLE,
        .gpio_num       = BLK_PWM_PIN,
        .duty           = 0, // Початковий стан: підсвічування вимкнене
        .hpoint         = 0
    };
    ledc_channel_config(&channel_conf);
}

// Плавне встановлення яскравості (від 0 до 100%)
void st7789_set_brightness(uint8_t percent)
{
    if (percent > 100) {
        percent = 100;
    }

    // Переведення лінійних відсотків у 10-бітне значення коефіцієнта заповнення (0..1023)
    uint32_t duty_val = (percent * 1023) / 100;

    ledc_set_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0, duty_val);
    ledc_update_duty(LEDC_LOW_SPEED_MODE, LEDC_CHANNEL_0);
}
