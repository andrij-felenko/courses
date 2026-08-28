static void provisioning_task(void *arg) {
    g_wifi_events = xEventGroupCreate();
    g_state = ST_BOOT;

    for (;;) {
        switch (g_state) {

        case ST_BOOT:
            // Розвилка: є збережена мережа — пропускаємо провізіонування.
            if (nvs_load_str("wifi_ssid", g_ssid, sizeof g_ssid) == ESP_OK &&
                g_ssid[0] != '\0') {
                nvs_load_str("wifi_pass", g_pass, sizeof g_pass);
                g_state = ST_PROVING;            // одразу пробуємо відому мережу
            } else {
                g_state = ST_PROVISION_AP;       // нічого не знаємо — у портал
            }
            break;

        case ST_PROVISION_AP:
            start_provisioning_ap();             // AP з унікальним SSID (зі статті)
            start_dns_captive();                 // DNS-пастка на 192.168.4.1
            start_http_form(g_last_fail_reason); // форма; напис помилки, якщо була
            // Спимо в цьому стані, доки обробник форми не заповнить кандидатів
            // і не переведе нас у ST_RECEIVED (через свій прапорець/чергу).
            wait_until_state_changes();
            break;

        case ST_RECEIVED:
            // Кандидати вже провалідовані обробником форми. Йдемо їх ДОВОДИТИ.
            g_state = ST_PROVING;
            break;

        case ST_PROVING:
            if (try_station_connect()) {
                // Перемога. АЖ ТЕПЕР фіксуємо в NVS і гасимо портал.
                nvs_save_str("wifi_ssid", g_ssid);
                nvs_save_str("wifi_pass", g_pass);
                stop_dns_captive();
                stop_http_form();
                esp_wifi_set_mode(WIFI_MODE_STA); // портал згас, лишаємось станцією
                g_state = ST_CONNECTED;
            } else {
                // Не довели. Вертаємось у портал — АЛЕ його не було, якщо ми
                // прийшли сюди прямо з BOOT (відома мережа зникла). Тоді підіймаємо.
                g_state = ST_PROVISION_AP;
            }
            break;

        case ST_CONNECTED:
            // Живемо в мережі. Тут — звичайна робота вузла; автомат провізіонування
            // своє зробив. Прокинеться знову лише від жесту скидання (нижче).
            wait_until_state_changes();
            break;
        }
    }
}
