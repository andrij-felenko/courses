// Віддати файл path із файлової системи (примонтованої в /spiffs).
static esp_err_t send_file_from_fs(httpd_req_t *req, const char *name)
{
    char full[64];
    snprintf(full, sizeof(full), "/spiffs/%s", name);
    FILE *f = fopen(full, "r");
    if (!f) {                                   // нема файлу — чесний 404
        httpd_resp_send_404(req);
        return ESP_FAIL;
    }

    // тип за розширенням — щоб браузер знав, як читати
    if (strstr(name, ".html"))      httpd_resp_set_type(req, "text/html");
    else if (strstr(name, ".css"))  httpd_resp_set_type(req, "text/css");
    else if (strstr(name, ".js"))   httpd_resp_set_type(req, "application/javascript");
    else                            httpd_resp_set_type(req, "text/plain");

    // віддаємо ПОРЦІЯМИ: великий файл не тримаємо в пам'яті цілком
    char chunk[512];
    size_t n;
    while ((n = fread(chunk, 1, sizeof(chunk), f)) > 0)
        httpd_resp_send_chunk(req, chunk, n);   // кожна порція — окремим шматком
    httpd_resp_send_chunk(req, NULL, 0);        // порожній шматок = «файл скінчився»

    fclose(f);
    return ESP_OK;
}
