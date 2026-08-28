// Повертає true, лише якщо STA-підключення ДОВЕЛО себе (дістали IP).
static bool try_station_connect(void) {
    // Кандидатів — у конфіг станції. AP при цьому НЕ чіпаємо: лишається живим.
    wifi_config_t sta = { 0 };
    strncpy((char *)sta.sta.ssid, g_ssid, sizeof sta.sta.ssid);
    strncpy((char *)sta.sta.password, g_pass, sizeof sta.sta.password);

    esp_wifi_set_mode(WIFI_MODE_APSTA);          // і портал, і станція водночас
    esp_wifi_set_config(WIFI_IF_STA, &sta);

    // Чистимо старі біти, щоб не спіймати відлуння минулої спроби.
    xEventGroupClearBits(g_wifi_events, BIT_GOT_IP | BIT_STA_FAILED);
    esp_wifi_connect();                          // асинхронно; вирок прилетить подією

    // Спимо, доки не прилетить доказ, відмова — або доки не сплине тайм-аут.
    const TickType_t timeout = pdMS_TO_TICKS(15000);   // ~15 с на всю спробу
    EventBits_t bits = xEventGroupWaitBits(
        g_wifi_events, BIT_GOT_IP | BIT_STA_FAILED,
        pdTRUE,   // очистити біти на виході
        pdFALSE,  // будь-який з бітів (не обов'язково обидва)
        timeout);

    if (bits & BIT_GOT_IP) {
        return true;                             // дістали IP — доведено
    }
    // Сюди — і за явної відмови, і за тиші (тайм-аут). І там, і там: не вдалося.
    if (!(bits & BIT_STA_FAILED)) {
        g_last_fail_reason = 0;                  // 0 = «мовчання», тобто тайм-аут
    }
    esp_wifi_disconnect();                        // прибрати недороблену спробу
    return false;
}
