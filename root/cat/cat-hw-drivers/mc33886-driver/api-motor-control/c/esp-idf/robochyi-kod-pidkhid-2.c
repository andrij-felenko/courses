// ── MC33886: ШІМ прямо на IN, EN ввімкнено. ESP32, ESP-IDF ──
// ОБИДВІ ніжки напрямку — на своїх каналах LEDC від ОДНОГО таймера,
// тож частота в них спільна. Активна модулюється, «мовчазна» тримає 0.

#include "driver/gpio.h"
#include "driver/ledc.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define PIN_IN1   GPIO_NUM_25
#define PIN_IN2   GPIO_NUM_26
#define PIN_EN    GPIO_NUM_27            // проста GPIO, тримаємо в «1»

#define PWM_MODE  LEDC_LOW_SPEED_MODE
#define CH_IN1    LEDC_CHANNEL_0
#define CH_IN2    LEDC_CHANNEL_1
#define DUTY_MAX  1023

static void ch_duty(ledc_channel_t ch, uint32_t duty) {
    ledc_set_duty(PWM_MODE, ch, duty);
    ledc_update_duty(PWM_MODE, ch);
}

static void motor_brake(void) {
    ch_duty(CH_IN1, 0);
    ch_duty(CH_IN2, 0);                  // 0 0 → тримаюче гальмо
}

static void motor_init(void) {
    ledc_timer_config_t tim = {
        .speed_mode = PWM_MODE, .timer_num = LEDC_TIMER_0,
        .duty_resolution = LEDC_TIMER_10_BIT,
        .freq_hz = 5000, .clk_cfg = LEDC_AUTO_CLK,
    };
    ESP_ERROR_CHECK(ledc_timer_config(&tim));

    ledc_channel_config_t ch = {        // обидві ніжки — ШІМ-канали
        .speed_mode = PWM_MODE, .timer_sel = LEDC_TIMER_0,
        .intr_type = LEDC_INTR_DISABLE, .duty = 0, .hpoint = 0,
    };
    ch.gpio_num = PIN_IN1; ch.channel = CH_IN1;
    ESP_ERROR_CHECK(ledc_channel_config(&ch));
    ch.gpio_num = PIN_IN2; ch.channel = CH_IN2;
    ESP_ERROR_CHECK(ledc_channel_config(&ch));

    gpio_set_direction(PIN_EN, GPIO_MODE_OUTPUT);
    gpio_set_level(PIN_EN, 1);           // міст живий увесь час
    motor_brake();
}

static void motor_forward(uint32_t duty) {
    ch_duty(CH_IN1, 0);                  // стала «0»
    ch_duty(CH_IN2, duty);               // модуляція → у паузах стан 0 0
}

static void motor_reverse(uint32_t duty) {
    ch_duty(CH_IN2, 0);
    ch_duty(CH_IN1, duty);
}

static void motor_coast(void) {
    gpio_set_level(PIN_EN, 0);           // вибіг — лише через EN
    motor_brake();
}

void app_main(void) {
    motor_init();
    for (;;) {
        gpio_set_level(PIN_EN, 1);
        motor_forward(720); vTaskDelay(pdMS_TO_TICKS(1500));
        motor_reverse(480); vTaskDelay(pdMS_TO_TICKS(1500));
        motor_brake();      vTaskDelay(pdMS_TO_TICKS(800));
    }
}
