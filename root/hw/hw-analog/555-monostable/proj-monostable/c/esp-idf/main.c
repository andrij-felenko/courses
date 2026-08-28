#include "driver/gpio.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define BTN_GPIO GPIO_NUM_4
#define OUT_GPIO GPIO_NUM_5

void debounce_task(void *arg) {
    gpio_config_t in = {                       // кнопка замикає вхід на землю
        .pin_bit_mask = 1ULL << BTN_GPIO,
        .mode         = GPIO_MODE_INPUT,
        .pull_up_en   = GPIO_PULLUP_ENABLE,
    };
    gpio_config(&in);
    gpio_config_t out = {                      // сюди виходить чистий імпульс
        .pin_bit_mask = 1ULL << OUT_GPIO,
        .mode         = GPIO_MODE_OUTPUT,
    };
    gpio_config(&out);

    oneshot_t btn;
    oneshot_init(&btn, 30);                    // T = 30 мс, трохи довше за брязкіт
    bool prev = true;

    for (;;) {
        bool level   = gpio_get_level(BTN_GPIO) != 0;   // 0 = натиснуто
        bool falling = prev && !level;
        prev = level;

        uint32_t now = (uint32_t)(esp_timer_get_time() / 1000);  // мкс → мс
        gpio_set_level(OUT_GPIO, oneshot_poll(&btn, falling, now));
        vTaskDelay(pdMS_TO_TICKS(1));          // крок опитування
    }
}
