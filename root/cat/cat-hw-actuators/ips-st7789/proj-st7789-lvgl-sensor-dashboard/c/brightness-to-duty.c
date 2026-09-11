#include <stdio.h>
#include <stdint.h>
#include "esp_err.h"
#include "driver/ledc.h"
#include "esp_timer.h"

// Конфігурація лінії BLK через периферійний блок LEDC
#define BACKLIGHT_GPIO          GPIO_NUM_4
#define BACKLIGHT_LEDC_TIMER    LEDC_TIMER_0
#define BACKLIGHT_LEDC_MODE     LEDC_LOW_SPEED_MODE
#define BACKLIGHT_LEDC_CHANNEL  LEDC_CHANNEL_0
#define BACKLIGHT_LEDC_FREQ_HZ  4000              // 4 кГц: без писку та стробування
#define BACKLIGHT_LEDC_RES      LEDC_TIMER_10_BIT // 10 біт: діапазон від 0 до 1023
#define BACKLIGHT_MAX_DUTY      ((1 << 10) - 1)

#define DIM_TIMEOUT_US          (30ULL * 1000 * 1000) // 30 секунд до затемнення
#define BRIGHTNESS_ACTIVE       100                   // 100% у робочому стані
#define BRIGHTNESS_DIMMED       12                    // 12% у черговому режимі

typedef enum {
    BACKLIGHT_STATE_ACTIVE,
    BACKLIGHT_STATE_DIMMED
} backlight_state_t;

static uint8_t s_current_brightness = 0;
static int64_t s_last_activity_time = 0;
static backlight_state_t s_state = BACKLIGHT_STATE_ACTIVE;

// Квадратична корекція яскравості для компенсації сприйняття ока
static uint32_t brightness_to_duty(uint8_t percent) {
    if (percent > 100) percent = 100;
    return ((uint32_t)percent * (uint32_t)percent * BACKLIGHT_MAX_DUTY) / 10000;
}

// Ініціалізація апаратного таймера та вихідного каналу ШІМ
esp_err_t backlight_init(void) {
    ledc_timer_config_t timer_conf = {
        .speed_mode       = BACKLIGHT_LEDC_MODE,
        .timer_num        = BACKLIGHT_LEDC_TIMER,
        .duty_resolution  = BACKLIGHT_LEDC_RES,
        .freq_hz          = BACKLIGHT_LEDC_FREQ_HZ,
        .clk_cfg          = LEDC_AUTO_CLK
    };
    esp_err_t ret = ledc_timer_config(&timer_conf);
    if (ret != ESP_OK) return ret;

    ledc_channel_config_t ch_conf = {
        .gpio_num       = BACKLIGHT_GPIO,
        .speed_mode     = BACKLIGHT_LEDC_MODE,
        .channel        = BACKLIGHT_LEDC_CHANNEL,
        .intr_type      = LEDC_INTR_DISABLE,
        .timer_sel      = BACKLIGHT_LEDC_TIMER,
        .duty           = 0, // Початково підсвічування вимкнено для плавного пуску
        .hpoint         = 0
    };
    ret = ledc_channel_config(&ch_conf);
    if (ret != ESP_OK) return ret;

    // Встановлюємо сервіс апаратного згасання/наростання
    ledc_fade_func_install(0);

    s_last_activity_time = esp_timer_get_time();
    s_state = BACKLIGHT_STATE_ACTIVE;

    // Плавний пуск (soft-start) від 0 до 100% за 250 мс
    uint32_t target_duty = brightness_to_duty(BRIGHTNESS_ACTIVE);
    ledc_set_fade_with_time(BACKLIGHT_LEDC_MODE, BACKLIGHT_LEDC_CHANNEL,
                            target_duty, 250);
    ledc_fade_start(BACKLIGHT_LEDC_MODE, BACKLIGHT_LEDC_CHANNEL, LEDC_FADE_NO_WAIT);
    s_current_brightness = BRIGHTNESS_ACTIVE;

    return ESP_OK;
}

// Встановлення цільової яскравості з керованим часом переходу
void backlight_set_brightness(uint8_t percent, uint32_t transition_ms) {
    if (percent > 100) percent = 100;
    uint32_t target_duty = brightness_to_duty(percent);

    if (transition_ms > 0) {
        ledc_set_fade_with_time(BACKLIGHT_LEDC_MODE, BACKLIGHT_LEDC_CHANNEL,
                                target_duty, transition_ms);
        ledc_fade_start(BACKLIGHT_LEDC_MODE, BACKLIGHT_LEDC_CHANNEL, LEDC_FADE_NO_WAIT);
    } else {
        ledc_set_duty(BACKLIGHT_LEDC_MODE, BACKLIGHT_LEDC_CHANNEL, target_duty);
        ledc_update_duty(BACKLIGHT_LEDC_MODE, BACKLIGHT_LEDC_CHANNEL);
    }
    s_current_brightness = percent;
}

// Реєстрація взаємодії з приладом (пробудження екрана)
void backlight_notify_activity(void) {
    s_last_activity_time = esp_timer_get_time();
    if (s_state != BACKLIGHT_STATE_ACTIVE) {
        s_state = BACKLIGHT_STATE_ACTIVE;
        backlight_set_brightness(BRIGHTNESS_ACTIVE, 150); // Пробудження за 150 мс
    }
}

// Фонова перевірка таймауту для переходу в черговий режим
void backlight_process(void) {
    int64_t now = esp_timer_get_time();
    if (s_state == BACKLIGHT_STATE_ACTIVE) {
        if ((now - s_last_activity_time) >= DIM_TIMEOUT_US) {
            s_state = BACKLIGHT_STATE_DIMMED;
            backlight_set_brightness(BRIGHTNESS_DIMMED, 500); // Плавне затемнення за 500 мс
        }
    }
}
