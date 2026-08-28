static void brownout_bookkeeping(esp_reset_reason_t reason)
{
    if (s_rtc_magic != RTC_MAGIC) {
        // Холодний старт (подали живлення) або сміття в RTC — ініціалізуємо.
        s_rtc_magic = RTC_MAGIC;
        s_brownout_count = 0;
        return;
    }
    // Пам'ять наша й достовірна. Якщо це був brownout — рахуємо.
    if (reason == ESP_RST_BROWNOUT) {
        s_brownout_count++;
        ESP_LOGE(TAG, "brownout #%u поспіль", (unsigned)s_brownout_count);
    } else if (reason == ESP_RST_POWERON) {
        // Живлення передумали й дали чисто — рахунок скидаємо.
        s_brownout_count = 0;
    }
    // Інші причини (панік, watchdog) рахунок brownout не чіпають.
}
