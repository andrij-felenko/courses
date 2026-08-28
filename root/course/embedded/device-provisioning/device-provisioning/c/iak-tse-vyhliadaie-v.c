// Ім'я точки доступу роблять унікальним — зазвичай із хвоста MAC-адреси,
// щоб два однакові пристрої поруч не злилися в одну назву.
static void start_provisioning_ap(void) {
    uint8_t mac[6];
    esp_wifi_get_mac(WIFI_IF_STA, mac);

    char ssid[32];
    snprintf(ssid, sizeof ssid, "Thermostat-%02X%02X", mac[4], mac[5]);

    wifi_config_t ap = { 0 };
    strncpy((char *)ap.ap.ssid, ssid, sizeof ap.ap.ssid);
    ap.ap.ssid_len  = strlen(ssid);
    ap.ap.channel   = 1;
    ap.ap.max_connection = 4;
    ap.ap.authmode  = WIFI_AUTH_OPEN;   // відкрита — щоб телефон під'єднався без пароля

    esp_wifi_set_mode(WIFI_MODE_AP);
    esp_wifi_set_config(WIFI_IF_AP, &ap);
    esp_wifi_start();
    // Тепер пристрій — точка доступу за адресою 192.168.4.1
}
