// Викликається веб-сервером, коли прийшла заповнена форма (метод POST).
static esp_err_t on_credentials_post(httpd_req_t *req) {
    char body[256];
    int len = httpd_req_recv(req, body, sizeof(body) - 1);
    if (len <= 0) return ESP_FAIL;
    body[len] = '\0';                       // робимо справжній C-рядок

    char ssid[33] = {0}, pass[65] = {0};
    // Розбираємо поля форми ssid=...&pass=...
    parse_form_field(body, "ssid", ssid, sizeof ssid);
    parse_form_field(body, "pass", pass, sizeof pass);

    // Чужому вводу не довіряй: порожня назва — не приймаємо
    if (ssid[0] == '\0') {
        httpd_resp_sendstr(req, "SSID порожній");
        return ESP_OK;
    }

    // Зберігаємо в NVS — щоб пережити перезавантаження й більше не питати
    nvs_save_str("wifi_ssid", ssid);
    nvs_save_str("wifi_pass", pass);

    httpd_resp_sendstr(req, "Прийнято. Пристрій під'єднується...");
    // Далі — погасити точку доступу й спробувати STA-підключення (див. замітку)
    schedule_switch_to_station();
    return ESP_OK;
}
