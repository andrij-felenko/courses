#include "esp_http_server.h"   // вбудований сервер ESP-IDF

// 1) Обробник головної сторінки: віддаємо готовий HTML (статику).
static esp_err_t home_get(httpd_req_t *req)
{
    const char *page =
        "<!DOCTYPE html><html><body>"
        "<h2>Мій пристрій</h2>"
        "<p>Температура: <span id='t'>--</span> °C</p>"
        "<script>"
        "setInterval(async()=>{"                 // раз на секунду питаємо /state
        "  let r=await fetch('/state');"
        "  let d=await r.json();"
        "  document.getElementById('t').textContent=d.temp;"
        "},1000);"
        "</script></body></html>";

    httpd_resp_set_type(req, "text/html");       // кажемо браузеру: це сторінка
    httpd_resp_sendstr(req, page);               // віддаємо тіло
    return ESP_OK;
}

// 2) Обробник даних: збираємо свіже показання й віддаємо JSON.
static esp_err_t state_get(httpd_req_t *req)
{
    float temp = read_temperature();             // реальне читання давача
    char json[64];
    snprintf(json, sizeof(json), "{\"temp\":%.1f}", temp);   // {"temp":24.3}

    httpd_resp_set_type(req, "application/json");   // кажемо: це дані, не сторінка
    httpd_resp_sendstr(req, json);
    return ESP_OK;
}

// 3) Запускаємо сервер і РЕЄСТРУЄМО обидва маршрути в таблиці.
httpd_handle_t start_web_server(void)
{
    httpd_config_t cfg = HTTPD_DEFAULT_CONFIG();
    httpd_handle_t server = NULL;
    if (httpd_start(&server, &cfg) != ESP_OK) return NULL;

    httpd_uri_t home  = { .uri="/",      .method=HTTP_GET, .handler=home_get  };
    httpd_uri_t state = { .uri="/state", .method=HTTP_GET, .handler=state_get };

    httpd_register_uri_handler(server, &home);   // рядок таблиці: GET / → home_get
    httpd_register_uri_handler(server, &state);  // рядок таблиці: GET /state → state_get
    return server;
}
