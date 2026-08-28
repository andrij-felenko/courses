// ── Крок 4: утримати рівні, вибрати пробудження, заснути ──────────────────
static void arm_and_sleep(void)
{
    // 4a. Утримати критичний рівень load switch крізь сон.
    //     Без цього пін "попливе" в сні → гілка може ожити → стрибок струму.
    gpio_hold_en(PIN_SENSOR_PWR);
    gpio_deep_sleep_hold_en();   // увімкнути утримання ЦИФРОВИХ пінів у deep-sleep

    // 4b. Джерело пробудження — з RTC-домену. ext1 працює навіть із
    //     ВИМКНЕНОЮ RTC-периферією, тож економніший за ext0.
    const uint64_t wake_mask = (1ULL << PIN_WAKE);
    esp_sleep_enable_ext1_wakeup(wake_mask, ESP_EXT1_WAKEUP_ANY_HIGH);

    // 4c. Явно вимкнути RTC-периферію: нам потрібен лише RTC-таймер/контролер.
    esp_sleep_pd_config(ESP_PD_DOMAIN_RTC_PERIPH, ESP_PD_OPTION_OFF);

    // 4d. (для WROVER) зняти зайвий струм крізь підтяжку GPIO12.
    //     На WROVER GPIO12 має зовнішню підтяжку + внутрішній pulldown —
    //     у сні крізь них тече струм. rtc_gpio_isolate обриває цей шлях.
    rtc_gpio_isolate(GPIO_NUM_12);

    ESP_LOGI(TAG, "vhodymo v deep-sleep");
    esp_deep_sleep_start();       // сюди код більше не повертається
}

// ── Повний чек-лист засинання: рівно чотири кроки, у жорсткому порядку ─────
void enter_deep_sleep(void)
{
    sensor_power_down();   // 1. приспати периферію по шині
    quiesce_signals();     // 2. опустити сигнали
    cut_sensor_branch();   // 3. зняти живлення гілки
    arm_and_sleep();       // 4. утримати, обрати пробудження, заснути
}
