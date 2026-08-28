// дуже рано в boot, ще до важкої ініціалізації
RTC_NOINIT_ATTR static int brownouts;    // переживає brownout/WDT/SW-reset
esp_reset_reason_t r = esp_reset_reason();

switch (r) {
  case ESP_RST_POWERON:                   // звичайний старт від живлення
    brownouts = 0;                        // лише тут .rtc_noinit іще «сміття» — ініціалізуємо самі
    break;
  case ESP_RST_BROWNOUT:
    brownouts++;                          // рахуємо просідання поспіль
    ESP_LOGW(TAG, "brownout #%d", brownouts);
    if (brownouts >= 3)
        enter_safe_mode();                // не вмикати помпу/радіо
    break;
  case ESP_RST_TASK_WDT:
  case ESP_RST_INT_WDT:
    ESP_LOGW(TAG, "watchdog: щось зависло");   // привід шукати блокування
    break;
  case ESP_RST_DEEPSLEEP:
    restore_context();                    // прокинулись — не ініціалізуємо все наново
    break;
  default:
    ESP_LOGI(TAG, "reset reason = %d", r);     // решта — просто в лог
}
