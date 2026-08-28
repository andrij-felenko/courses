// Кнопка на GPIO0, притиснута до землі (активний рівень — 0).
#define BTN_GPIO        GPIO_NUM_0
#define HOLD_MS         10000   // 10 секунд суцільного утримання

static void reset_button_task(void *arg) {
    int64_t pressed_since = 0;    // мітка часу, коли кнопку притиснули (0 = відпущена)

    for (;;) {
        bool down = (gpio_get_level(BTN_GPIO) == 0);   // 0 = притиснута
        int64_t now = esp_timer_get_time() / 1000;     // мс від старту

        if (down) {
            if (pressed_since == 0) {
                pressed_since = now;                   // щойно притиснули — засікаємо
            } else if (now - pressed_since >= HOLD_MS) {
                // Тримали суцільно 10 с — це свідомий жест, не випадковий дотик.
                nvs_erase_key("wifi_ssid");
                nvs_erase_key("wifi_pass");
                esp_restart();                         // перезавантаження «з коробки»
            }
        } else {
            pressed_since = 0;    // відпустили (або деренч розімкнув) — лічильник з нуля
        }
        vTaskDelay(pdMS_TO_TICKS(50));   // опитуємо 20 разів на секунду — деренч гасне сам
    }
}
