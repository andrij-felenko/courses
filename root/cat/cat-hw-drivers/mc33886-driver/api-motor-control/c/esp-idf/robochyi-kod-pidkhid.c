// ── MC33886: керування мотором. ESP32, ESP-IDF (driver/ledc.h) ──
// EN сидить на каналі LEDC: свою частоту й розрядність задаємо явно.
// Швидкість — ledc_set_duty + ledc_update_duty; напрямок — рівні GPIO.

#include "driver/gpio.h"
#include "driver/ledc.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define PIN_IN1   GPIO_NUM_25            // напрямок, будь-яка GPIO-вихід
#define PIN_IN2   GPIO_NUM_26
#define PIN_EN    GPIO_NUM_27            // будь-яка GPIO — LEDC прив'яже сам

#define PWM_MODE  LEDC_LOW_SPEED_MODE
#define PWM_CHAN  LEDC_CHANNEL_0
#define PWM_TIMER LEDC_TIMER_0
#define DUTY_MAX  1023                   // 10 біт → шкала 0..1023

static void motor_duty(uint32_t duty) {  // одна ручка швидкості
    ledc_set_duty(PWM_MODE, PWM_CHAN, duty);
    ledc_update_duty(PWM_MODE, PWM_CHAN);
}

static void motor_coast(void) { motor_duty(0); }  // EN=0 → тристейт, вибіг

static void motor_init(void) {
    gpio_config_t io = {
        .pin_bit_mask = (1ULL << PIN_IN1) | (1ULL << PIN_IN2),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    ESP_ERROR_CHECK(gpio_config(&io));

    ledc_timer_config_t tim = {
        .speed_mode = PWM_MODE, .timer_num = PWM_TIMER,
        .duty_resolution = LEDC_TIMER_10_BIT,
        .freq_hz = 5000,             // 5 кГц: у межах ≤10 кГц чипа, поза чутним
        .clk_cfg = LEDC_AUTO_CLK,
    };
    ESP_ERROR_CHECK(ledc_timer_config(&tim));

    ledc_channel_config_t ch = {
        .gpio_num = PIN_EN, .speed_mode = PWM_MODE, .channel = PWM_CHAN,
        .timer_sel = PWM_TIMER, .intr_type = LEDC_INTR_DISABLE,
        .duty = 0, .hpoint = 0,
    };
    ESP_ERROR_CHECK(ledc_channel_config(&ch));
    motor_coast();                   // старт у безпечному стані: міст вимкнено
}

// duty: 0..DUTY_MAX — шпаруватість ШІМ (частка від 2^біт, не вольти).
static void motor_forward(uint32_t duty) {
    gpio_set_level(PIN_IN1, 0);
    gpio_set_level(PIN_IN2, 1);      // OUT1=−, OUT2=+  → один бік
    motor_duty(duty);
}

static void motor_reverse(uint32_t duty) {
    gpio_set_level(PIN_IN1, 1);
    gpio_set_level(PIN_IN2, 0);      // OUT1=+, OUT2=−  → інший бік
    motor_duty(duty);
}

static void motor_brake(void) {
    gpio_set_level(PIN_IN1, 0);
    gpio_set_level(PIN_IN2, 0);      // 0 0 → активне гальмо
    motor_duty(DUTY_MAX);            // міст має бути ВВІМКНЕНИЙ, щоб коротити
}

void app_main(void) {
    motor_init();
    for (;;) {
        motor_forward(720); vTaskDelay(pdMS_TO_TICKS(1500));  // ~70% від 1023
        motor_coast();      vTaskDelay(pdMS_TO_TICKS(800));
        motor_reverse(480); vTaskDelay(pdMS_TO_TICKS(1500));
        motor_brake();      vTaskDelay(pdMS_TO_TICKS(800));
    }
}
