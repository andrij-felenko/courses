static void wifi_event_handler(void *arg, esp_event_base_t base,
                               int32_t id, void *data) {
    // Дістали IP у режимі станції — це ЄДИНИЙ надійний доказ, що ми в мережі.
    if (base == IP_EVENT && id == IP_EVENT_STA_GOT_IP) {
        xEventGroupSetBits(g_wifi_events, BIT_GOT_IP);
        return;
    }

    // STA відвалилось. Тут два випадки, і їх варто розрізнити.
    if (base == WIFI_EVENT && id == WIFI_EVENT_STA_DISCONNECTED) {
        wifi_event_sta_disconnected_t *d = data;
        g_last_fail_reason = d->reason;

        // Поки ми ще ПЕРЕВІРЯЄМО (PROVING) — не влаштовуємо шторм повторів.
        // Даємо рівно кілька спроб, бо перший disconnect часто хибний.
        if (g_state == ST_PROVING) {
            static int retries;
            // 201 = NO_AP_FOUND: мережі просто нема — далі пробувати марно.
            if (d->reason == WIFI_REASON_NO_AP_FOUND || ++retries >= 3) {
                retries = 0;
                xEventGroupSetBits(g_wifi_events, BIT_STA_FAILED);
            } else {
                esp_wifi_connect();   // ще одна спроба (авт. таймінг рукостискання)
            }
        }
        // У стані CONNECTED (уже живемо в мережі) — окрема логіка переприєднання,
        // це вже знайоме нам швидке підключення, тут його не дублюємо.
        return;
    }
}
