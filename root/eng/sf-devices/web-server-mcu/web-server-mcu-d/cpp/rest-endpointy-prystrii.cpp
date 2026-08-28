// POST /led з тілом {"on":true} — прочитати тіло й перемкнути світло.
static esp_err_t led_post(httpd_req_t *req)
{
    char body[64];
    int total = req->content_len;               // скільки байтів тіла обіцяно
    if (total >= (int)sizeof(body)) {           // захист від завеликого тіла
        httpd_resp_send_err(req, HTTPD_400_BAD_REQUEST, "тіло завелике");
        return ESP_FAIL;
    }
    int got = httpd_req_recv(req, body, total); // читаємо тіло з сокета
    if (got <= 0) return ESP_FAIL;
    body[got] = '\0';

    bool on = strstr(body, "true") != NULL;     // (у житті — нормальний розбір JSON)
    set_led(on);

    httpd_resp_set_type(req, "application/json");
    httpd_resp_sendstr(req, on ? "{\"led\":true}" : "{\"led\":false}");
    return ESP_OK;
}
