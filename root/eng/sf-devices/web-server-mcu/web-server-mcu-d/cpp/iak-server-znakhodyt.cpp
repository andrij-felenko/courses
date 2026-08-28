// Хендлер на гілку /static/* — один обробник віддає будь-який файл звідти.
static esp_err_t static_get(httpd_req_t *req)
{
    // req->uri = "/static/app.js" → відрізаємо префікс, лишається "app.js"
    const char *path = req->uri + strlen("/static/");
    return send_file_from_fs(req, path);     // читаємо файл і віддаємо (нижче)
}

// Хендлер із параметром запиту: /led?state=on
static esp_err_t led_get(httpd_req_t *req)
{
    char buf[16] = {0};
    size_t qlen = httpd_req_get_url_query_len(req) + 1;
    if (qlen > 1 && qlen <= sizeof(buf)) {
        char query[16];
        httpd_req_get_url_query_str(req, query, qlen);          // "state=on"
        char val[8];
        if (httpd_query_key_value(query, "state", val, sizeof(val)) == ESP_OK)
            set_led(strcmp(val, "on") == 0);                    // вмикаємо/вимикаємо
    }
    httpd_resp_sendstr(req, "ok");
    return ESP_OK;
}
