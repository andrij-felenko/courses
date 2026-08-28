#include "driver/gpio.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define PIN_LED  GPIO_NUM_18
#define PIN_BTN  GPIO_NUM_19

#define DEBOUNCE_MS  30                 // поріг: скільки чекати, поки брязкіт уляжеться

static uint32_t now_ms(void) {          // монотонний годинник від старту, у мілісекундах
    return (uint32_t)(esp_timer_get_time() / 1000);
}

void app_main(void) {
    gpio_config_t out = { .pin_bit_mask = 1ULL << PIN_LED, .mode = GPIO_MODE_OUTPUT };
    gpio_config(&out);
    gpio_config_t in = {
        .pin_bit_mask = 1ULL << PIN_BTN,
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
    };
    gpio_config(&in);

    bool     led_on    = false;         // поточний стан світла (перемикач)
    int      btn_stable = 1;            // останній «усталений» стан кнопки (відпущена = 1)
    int      btn_last   = 1;            // що прочитали минулого разу (для лову зміни)
    uint32_t last_edge  = 0;            // мить останнього дрижання на вході

    while (1) {
        int reading = gpio_get_level(PIN_BTN);

        // будь-яка зміна на вході — чи то натиск, чи то брязкіт — заводить годинник наново
        if (reading != btn_last) {
            last_edge = now_ms();
        }

        // вхід постояв незмінним досить довго — йому вже можна вірити
        if (now_ms() - last_edge > DEBOUNCE_MS) {
            if (reading != btn_stable) {
                btn_stable = reading;
                if (btn_stable == 0) {          // саме натиснули (active-low)
                    led_on = !led_on;           // перевертаємо світло
                    gpio_set_level(PIN_LED, led_on ? 1 : 0);
                }
            }
        }

        btn_last = reading;             // запам'ятали для наступного кола
        vTaskDelay(pdMS_TO_TICKS(2));   // опитуємо часто, але віддаємо час іншим задачам
    }
}
