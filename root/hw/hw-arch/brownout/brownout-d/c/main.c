RTC_NOINIT_ATTR static uint32_t s_brownout_cnt;   // окремий лічильник просідань
RTC_NOINIT_ATTR static uint32_t s_panic_cnt;      // окремий лічильник panic

void startup_analyze_reset(void) {
    esp_reset_reason_t reason = esp_reset_reason();

    switch (reason) {
    case ESP_RST_POWERON:
        // Справжній холодний старт — обидва лічильники в нуль
        s_brownout_cnt = 0;
        s_panic_cnt    = 0;
        break;

    case ESP_RST_BROWNOUT:
        s_brownout_cnt++;
        ESP_LOGW(TAG, "brownout reset #%lu — check power supply!", s_brownout_cnt);
        if (s_brownout_cnt >= 3) {              // серія просідань поспіль
            ESP_LOGW(TAG, "repeated brownout — reducing WiFi TX power");
            wifi_tx_power_reduce();             // знизити струм радіо, не чіпати прошивку
        }
        nvs_set_u32(nvs_h, "brownout_cnt", s_brownout_cnt);  // для звіту користувачу
        nvs_commit(nvs_h);
        break;

    case ESP_RST_TASK_WDT:
    case ESP_RST_INT_WDT:
    case ESP_RST_PANIC:
        s_panic_cnt++;
        ESP_LOGE(TAG, "watchdog/panic reset #%lu", s_panic_cnt);
        if (s_panic_cnt >= FAULT_THRESHOLD) {  // серія крахів коду
            config_rollback_if_available();    // відкат конфіга/прошивки
        }
        break;

    default:
        break;
    }
}
