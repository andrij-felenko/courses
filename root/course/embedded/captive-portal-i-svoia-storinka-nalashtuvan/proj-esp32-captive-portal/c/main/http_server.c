#include "http_server.h"

#include <stdlib.h>
#include <string.h>

#include "cJSON.h"
#include "config_store.h"
#include "deferred_reboot.h"
#include "esp_log.h"
#include "wifi_ap.h"

static const char *TAG = "http";

/* Куди відправляємо клієнта з будь-якого перехопленого зонда. */
#define SETUP_URL "http://" WIFI_AP_IP_ADDR "/setup"

/* Тіло POST /api/save: два рядки й обгортка JSON — 256 байтів вистачає. */
#define SAVE_BODY_MAX 256

/* Скільки разів терпимо тайм-аут читання тіла, перш ніж кинути клієнта. */
#define RECV_RETRIES 3

/* Пауза перед перезапуском: стек TCP/IP має встигнути віддати відповідь. */
#define REBOOT_DELAY_MS 2000

/*
 * Сторінка потрапляє у прошивку стисненою, секцією .rodata. Віддаємо її
 * прямо з Flash за принципом zero-copy: жодного проміжного буфера в RAM,
 * а браузер розтискає потік сам, побачивши Content-Encoding: gzip.
 */
extern const uint8_t index_html_gz_start[] asm("_binary_index_html_gz_start");
extern const uint8_t index_html_gz_end[] asm("_binary_index_html_gz_end");

/*
 * Сторінка майстра не має кешуватися: інакше після перезавантаження
 * пристрою браузер покаже її ж замість справжнього вмісту мережі.
 */
static void set_no_cache(httpd_req_t *req)
{
    httpd_resp_set_hdr(req, "Cache-Control", "no-cache, no-store, must-revalidate");
    httpd_resp_set_hdr(req, "Pragma", "no-cache");
}

static esp_err_t send_json_error(httpd_req_t *req, const char *status, const char *message)
{
    cJSON *root = cJSON_CreateObject();
    if (root == NULL) {
        return httpd_resp_send_500(req);
    }
    cJSON_AddStringToObject(root, "status", "error");
    cJSON_AddStringToObject(root, "message", message);

    char *body = cJSON_PrintUnformatted(root);
    cJSON_Delete(root);
    if (body == NULL) {
        return httpd_resp_send_500(req);
    }

    httpd_resp_set_status(req, status);
    httpd_resp_set_type(req, "application/json");
    set_no_cache(req);
    const esp_err_t err = httpd_resp_sendstr(req, body);

    cJSON_free(body);
    return err;
}

/* --- Перехоплення зондів ------------------------------------------------ */

/*
 * Сюди потрапляє все, що не збіглося з точними маршрутами: /generate_204
 * і /gen_204 від Android, /hotspot-detect.html від Apple, /ncsi.txt та
 * /connecttest.txt від Windows — і будь-яка адреса, набрана вручну.
 *
 * Відповідь 302 з полем Location і є сигналом «мережа за порталом»:
 * система бачить не той код, що чекала (204 або 200 з відомим тілом),
 * і сама відкриває вікно входу.
 */
static esp_err_t captive_redirect_handler(httpd_req_t *req)
{
    ESP_LOGI(TAG, "Зонд %s → 302 на майстра", req->uri);

    httpd_resp_set_status(req, "302 Found");
    httpd_resp_set_hdr(req, "Location", SETUP_URL);
    set_no_cache(req);
    return httpd_resp_send(req, NULL, 0);
}

/* --- Сторінка майстра --------------------------------------------------- */

static esp_err_t setup_page_handler(httpd_req_t *req)
{
    const size_t gz_len = (size_t)(index_html_gz_end - index_html_gz_start);

    httpd_resp_set_type(req, "text/html");
    httpd_resp_set_hdr(req, "Content-Encoding", "gzip");
    set_no_cache(req);
    return httpd_resp_send(req, (const char *)index_html_gz_start, gz_len);
}

/* --- GET /api/scan ------------------------------------------------------ */

static esp_err_t api_scan_handler(httpd_req_t *req)
{
    static wifi_ap_record_t records[WIFI_SCAN_MAX_RECORDS];
    uint16_t count = WIFI_SCAN_MAX_RECORDS;

    const esp_err_t scan_err = wifi_ap_scan(records, &count);
    if (scan_err != ESP_OK) {
        return send_json_error(req, "503 Service Unavailable", "scan failed");
    }

    cJSON *root = cJSON_CreateObject();
    cJSON *list = cJSON_CreateArray();
    if (root == NULL || list == NULL) {
        cJSON_Delete(root);
        cJSON_Delete(list);
        return httpd_resp_send_500(req);
    }
    cJSON_AddItemToObject(root, "networks", list);

    for (uint16_t i = 0; i < count; i++) {
        cJSON *item = cJSON_CreateObject();
        if (item == NULL) {
            break;
        }
        /* SSID у структурі драйвера — масив на 33 байти з нулем у кінці. */
        cJSON_AddStringToObject(item, "ssid", (const char *)records[i].ssid);
        cJSON_AddNumberToObject(item, "rssi", records[i].rssi);
        cJSON_AddNumberToObject(item, "channel", records[i].primary);
        cJSON_AddStringToObject(item, "auth", wifi_auth_name(records[i].authmode));
        cJSON_AddItemToArray(list, item);
    }

    char *body = cJSON_PrintUnformatted(root);
    cJSON_Delete(root);
    if (body == NULL) {
        return httpd_resp_send_500(req);
    }

    httpd_resp_set_type(req, "application/json");
    set_no_cache(req);
    const esp_err_t err = httpd_resp_sendstr(req, body);

    cJSON_free(body);
    return err;
}

/* --- POST /api/save ----------------------------------------------------- */

static esp_err_t receive_body(httpd_req_t *req, char *buf, size_t capacity)
{
    if (req->content_len == 0 || req->content_len >= capacity) {
        return ESP_ERR_INVALID_SIZE;
    }

    size_t received = 0;
    int retries = RECV_RETRIES;

    while (received < req->content_len) {
        const int chunk = httpd_req_recv(req, buf + received, req->content_len - received);
        if (chunk == HTTPD_SOCK_ERR_TIMEOUT) {
            /* Клієнт замовк: даємо кілька спроб і звільняємо сокет. */
            if (--retries > 0) {
                continue;
            }
            return ESP_ERR_TIMEOUT;
        }
        if (chunk <= 0) {
            return ESP_FAIL;
        }
        received += (size_t)chunk;
    }

    buf[received] = '\0';
    return ESP_OK;
}

static esp_err_t api_save_handler(httpd_req_t *req)
{
    char body[SAVE_BODY_MAX];

    const esp_err_t recv_err = receive_body(req, body, sizeof(body));
    if (recv_err == ESP_ERR_INVALID_SIZE) {
        return send_json_error(req, "413 Payload Too Large", "body too large");
    }
    if (recv_err != ESP_OK) {
        return send_json_error(req, "400 Bad Request", "incomplete body");
    }

    cJSON *root = cJSON_Parse(body);
    if (root == NULL) {
        return send_json_error(req, "400 Bad Request", "malformed json");
    }

    const cJSON *j_ssid = cJSON_GetObjectItem(root, "ssid");
    const cJSON *j_pass = cJSON_GetObjectItem(root, "password");

    if (!cJSON_IsString(j_ssid)) {
        cJSON_Delete(root);
        return send_json_error(req, "400 Bad Request", "ssid required");
    }

    const char *ssid = j_ssid->valuestring;
    const size_t ssid_len = strlen(ssid);
    if (ssid_len == 0 || ssid_len > CONFIG_STORE_SSID_MAX) {
        cJSON_Delete(root);
        return send_json_error(req, "400 Bad Request", "ssid length 1..32");
    }

    const char *password = cJSON_IsString(j_pass) ? j_pass->valuestring : "";
    const size_t pass_len = strlen(password);
    /* Порожній пароль означає відкриту мережу; WPA2 коротших за 8 не знає. */
    if (pass_len != 0 && (pass_len < 8 || pass_len > CONFIG_STORE_PASS_MAX)) {
        cJSON_Delete(root);
        return send_json_error(req, "400 Bad Request", "password length 8..63");
    }

    const esp_err_t save_err = config_store_save(ssid, password);
    cJSON_Delete(root);

    if (save_err != ESP_OK) {
        return send_json_error(req, "500 Internal Server Error", "nvs write failed");
    }

    httpd_resp_set_type(req, "application/json");
    set_no_cache(req);
    const esp_err_t err = httpd_resp_sendstr(
        req, "{\"status\":\"ok\",\"message\":\"saved\",\"reboot_ms\":2000}");

    /*
     * Таймер заводимо після відправлення відповіді, але перезапуск однаково
     * відкладений: httpd_resp_sendstr лише передає дані стеку TCP/IP,
     * а той ще має дочекатися підтвердження від клієнта.
     */
    deferred_reboot_schedule(REBOOT_DELAY_MS);
    return err;
}

/* --- Запуск ------------------------------------------------------------- */

esp_err_t http_server_init(httpd_handle_t *out_server)
{
    if (out_server == NULL) {
        return ESP_ERR_INVALID_ARG;
    }
    *out_server = NULL;

    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.stack_size = 4096;       /* заголовки, парсинг JSON, форматування відповіді */
    config.max_uri_handlers = 8;
    config.max_open_sockets = 4;    /* 1 UDP DNS живе поза сервером, тут — TCP-клієнти */
    config.lru_purge_enable = true; /* новий клієнт витісняє найдавнішого, а не отримує відмову */

    /*
     * Телефон, що вимкнув екран або вийшов із зони, не встигає надіслати
     * FIN. З'єднання лишилося б у ESTABLISHED до спрацьовування keep-alive,
     * а чотирьох таких досить, щоб сервер перестав приймати нових.
     * Тайм-аути кладуть на сокет SO_RCVTIMEO/SO_SNDTIMEO і закривають
     * мертву сесію за п'ять секунд.
     */
    config.recv_wait_timeout = 5;
    config.send_wait_timeout = 5;

    /* Без цього збігача шаблон із зірочкою лишився б звичайним рядком. */
    config.uri_match_fn = httpd_uri_match_wildcard;

    httpd_handle_t server = NULL;
    const esp_err_t err = httpd_start(&server, &config);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "httpd_start: %s", esp_err_to_name(err));
        return err;
    }

    /*
     * Порядок реєстрації важить: збігач перебирає маршрути так, як їх
     * додали, тож універсальний перехоплювач має стояти останнім —
     * інакше він з'їв би й /setup, і REST.
     */
    const httpd_uri_t routes[] = {
        {.uri = "/",          .method = HTTP_GET,  .handler = setup_page_handler},
        {.uri = "/setup",     .method = HTTP_GET,  .handler = setup_page_handler},
        {.uri = "/api/scan",  .method = HTTP_GET,  .handler = api_scan_handler},
        {.uri = "/api/save",  .method = HTTP_POST, .handler = api_save_handler},
        {.uri = "/*",         .method = HTTP_GET,  .handler = captive_redirect_handler},
    };

    for (size_t i = 0; i < sizeof(routes) / sizeof(routes[0]); i++) {
        const esp_err_t reg_err = httpd_register_uri_handler(server, &routes[i]);
        if (reg_err != ESP_OK) {
            ESP_LOGE(TAG, "Маршрут %s не зареєстровано: %s",
                     routes[i].uri, esp_err_to_name(reg_err));
            httpd_stop(server);
            return reg_err;
        }
    }

    ESP_LOGI(TAG, "Веб-сервер порталу слухає порт %d", config.server_port);
    *out_server = server;
    return ESP_OK;
}

void http_server_stop(httpd_handle_t server)
{
    if (server != NULL) {
        httpd_stop(server);
    }
}
