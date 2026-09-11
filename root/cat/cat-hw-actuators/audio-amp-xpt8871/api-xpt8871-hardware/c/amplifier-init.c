// Керування виводом SHDN мікросхеми XPT8871 в середовищі ESP-IDF
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "driver/ledc.h"

#define PIN_SHDN       GPIO_NUM_4
#define PIN_AUDIO      GPIO_NUM_18
#define LEDC_TIMER     LEDC_TIMER_0
#define LEDC_MODE      LEDC_LOW_SPEED_MODE
#define LEDC_CHANNEL   LEDC_CHANNEL_0

void amplifier_init(void) {
    // Налаштування виводу SHDN на вихід із підтяжкою догори
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << PIN_SHDN),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    gpio_config(&io_conf);
    gpio_set_level(PIN_SHDN, 1); // Початковий стан: глибокий сон

    // Налаштування таймера ШІМ для генерації звуку
    ledc_timer_config_t timer_conf = {
        .speed_mode = LEDC_MODE,
        .duty_resolution = LEDC_TIMER_10_BIT,
        .timer_num = LEDC_TIMER,
        .freq_hz = 1000,
        .clk_cfg = LEDC_AUTO_CLK
    };
    ledc_timer_config(&timer_conf);

    ledc_channel_config_t ch_conf = {
        .gpio_num = PIN_AUDIO,
        .speed_mode = LEDC_MODE,
        .channel = LEDC_CHANNEL,
        .intr_type = LEDC_INTR_DISABLE,
        .timer_sel = LEDC_TIMER,
        .duty = 0,
        .hpoint = 0
    };
    ledc_channel_config(&ch_conf);
}

void amplifier_wake(void) {
    gpio_set_level(PIN_SHDN, 0);                 // Переводимо SHDN у низький рівень
    vTaskDelay(pdMS_TO_TICKS(50));               // Затримка 50 мс для плавного заряду BYPASS
}

void amplifier_sleep(void) {
    vTaskDelay(pdMS_TO_TICKS(10));               // Пауза 10 мс для заспокоєння виходу
    gpio_set_level(PIN_SHDN, 1);                 // Вимикаємо підсилювач у сон
}

void play_alert(uint32_t freq_hz, uint32_t duration_ms) {
    amplifier_wake();                            // 1. Пробуджуємо та чекаємо стабілізації
    ledc_set_freq(LEDC_MODE, LEDC_TIMER, freq_hz);
    ledc_set_duty(LEDC_MODE, LEDC_CHANNEL, 512); // Шпаруватість 50%
    ledc_update_duty(LEDC_MODE, LEDC_CHANNEL);
    vTaskDelay(pdMS_TO_TICKS(duration_ms));      // 2. Звучання
    ledc_set_duty(LEDC_MODE, LEDC_CHANNEL, 0);   // 3. Зняття сигналу в нуль
    ledc_update_duty(LEDC_MODE, LEDC_CHANNEL);
    amplifier_sleep();                           // 4. Пауза та сон
}
