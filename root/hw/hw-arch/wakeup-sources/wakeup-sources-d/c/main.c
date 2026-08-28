#include "esp_sleep.h"
#include "driver/gpio.h"

#define WAKE_GPIO     GPIO_NUM_36          // мусить бути RTC-здатною ніжкою!
#define SLEEP_MINUTES 15
#define US_PER_MIN    60000000ULL          // мікросекунд у хвилині

void app_main(void) {
    // 1. Чому нас підняли?
    switch (esp_sleep_get_wakeup_cause()) {
        case ESP_SLEEP_WAKEUP_TIMER:        // сплив період
            handle_periodic_measurement();
            break;
        case ESP_SLEEP_WAKEUP_EXT0:         // натиснули кнопку
            handle_button_press();
            break;
        default:                            // перше холодне ввімкнення
            cold_start_init();
            break;
    }

    // 2. Вмикаємо ОБИДВА сторожі перед сном.
    esp_sleep_enable_timer_wakeup(SLEEP_MINUTES * US_PER_MIN);
    esp_sleep_enable_ext0_wakeup(WAKE_GPIO, 0);   // рівень 0 (LOW) будить

    // 3. У глибокий сон — прокинемося від того, що настане раніше.
    esp_deep_sleep_start();
    // Рядки нижче не виконуються: deep-sleep перезапускає чип з app_main().
}
