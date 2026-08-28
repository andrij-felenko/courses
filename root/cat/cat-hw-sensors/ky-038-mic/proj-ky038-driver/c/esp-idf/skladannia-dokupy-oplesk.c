#define PIN_DO       GPIO_NUM_4
#define PIN_OUT      GPIO_NUM_2         // те, чим керуємо (світлодіод/реле)
#define CLAP_WINDOW  300                // придушення торохтіння одного оплеску
#define DOUBLE_GAP   600                // максимум між двома оплесками пари

void clap_switch_task(void *arg) {
    bool was_sound = false, output_on = false;
    uint32_t last_clap = 0;
    uint8_t  clap_count = 0;

    for (;;) {
        bool is_sound = (gpio_get_level(PIN_DO) != idle_level);
        uint32_t now = (uint32_t)(esp_timer_get_time() / 1000);

        if (is_sound && !was_sound && now - last_clap > CLAP_WINDOW) {
            // зарахований новий оплеск
            if (now - last_clap < DOUBLE_GAP) clap_count++;   // близько до попереднього — пара
            else                              clap_count = 1; // задалеко — лічба спершу
            last_clap = now;

            if (clap_count >= 2) {          // два оплески поспіль — перемикаємось
                output_on = !output_on;
                gpio_set_level(PIN_OUT, output_on);
                clap_count = 0;             // щоб потрійний не порахувався ще раз
                ESP_LOGI(TAG, "%s", output_on ? "УВІМК" : "ВИМК");
            }
        }
        was_sound = is_sound;
        vTaskDelay(pdMS_TO_TICKS(2));
    }
}
