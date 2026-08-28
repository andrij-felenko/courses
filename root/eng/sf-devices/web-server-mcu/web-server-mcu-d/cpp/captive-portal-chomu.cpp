// Будь-який невідомий шлях під час налаштування → перенаправлення на форму.
static esp_err_t redirect_to_portal(httpd_req_t *req, httpd_err_code_t err)
{
    httpd_resp_set_status(req, "302 Found");
    httpd_resp_set_hdr(req, "Location", "http://192.168.4.1/");  // адреса пристрою-AP
    httpd_resp_send(req, NULL, 0);
    return ESP_OK;
}
// реєструємо як обробник «не знайдено», щоб ловити геть усі чужі шляхи:
// httpd_register_err_handler(server, HTTPD_404_NOT_FOUND, redirect_to_portal);
