#include <stdlib.h>
#include <string.h>
#include "esp_http_server.h"
#include "esp_wifi.h"
#include "esp_log.h"
#include "esp_system.h"
#include "nvs_flash.h"
#include "nvs.h"
#include "cJSON.h"
#include "freertos/FreeRTOS.h"
#include "freertos/timers.h"

static const char *TAG_HTTP = "http_server";
static TimerHandle_t s_reboot_timer = NULL;

extern const uint8_t index_html_gz_start[] asm("_binary_index_html_gz_start");
extern const uint8_t index_html_gz_end[]   asm("_binary_index_html_gz_end");

static void reboot_timer_callback(TimerHandle_t xTimer) {
    ESP_LOGI(TAG_HTTP, "Плановий перезапуск системи...");
    esp_restart();
}

static esp_err_t redirect_to_setup_handler(httpd_req_t *req) {
    httpd_resp_set_status(req, "302 Found");
    httpd_resp_set_hdr(req, "Location", "http://192.168.4.1/setup");
    httpd_resp_set_hdr(req, "Cache-Control", "no-cache, no-store, must-revalidate");
    httpd_resp_send(req, NULL, 0);
    return ESP_OK;
}

static esp_err_t setup_page_handler(httpd_req_t *req) {
    size_t gz_len = index_html_gz_end - index_html_gz_start;
    httpd_resp_set_type(req, "text/html");
    httpd_resp_set_hdr(req, "Content-Encoding", "gzip");
    httpd_resp_set_hdr(req, "Cache-Control", "no-cache, no-store, must-revalidate");
    httpd_resp_send(req, (const char *)index_html_gz_start, gz_len);
    return ESP_OK;
}

static esp_err_t api_scan_handler(httpd_req_t *req) {
    wifi_scan_config_t scan_config = {
        .ssid = 0, .bssid = 0, .channel = 0, .show_hidden = false
    };
    esp_wifi_scan_start(&scan_config, true);

    uint16_t ap_count = 0;
    esp_wifi_scan_get_ap_num(&ap_count);
    if (ap_count > 16) ap_count = 16;

    wifi_ap_record_t *ap_records = (wifi_ap_record_t *)malloc(sizeof(wifi_ap_record_t) * ap_count);
    if (!ap_records) {
        httpd_resp_send_500(req);
        return ESP_FAIL;
    }
    esp_wifi_scan_get_ap_records(&ap_count, ap_records);

    cJSON *root = cJSON_CreateObject();
    cJSON *list = cJSON_CreateArray();

    for (int i = 0; i < ap_count; i++) {
        cJSON *item = cJSON_CreateObject();
        cJSON_AddStringToObject(item, "ssid", (const char *)ap_records[i].ssid);
        cJSON_AddNumberToObject(item, "rssi", ap_records[i].rssi);
        cJSON_AddNumberToObject(item, "channel", ap_records[i].primary);
        cJSON_AddItemToArray(list, item);
    }
    free(ap_records);

    cJSON_AddItemToObject(root, "networks", list);
    const char *json_str = cJSON_PrintUnformatted(root);

    httpd_resp_set_type(req, "application/json");
    httpd_resp_set_hdr(req, "Cache-Control", "no-cache, no-store, must-revalidate");
    httpd_resp_sendstr(req, json_str);

    free((void *)json_str);
    cJSON_Delete(root);
    return ESP_OK;
}

static esp_err_t api_save_handler(httpd_req_t *req) {
    char buf[256];
    int ret = httpd_req_recv(req, buf, sizeof(buf) - 1);
    if (ret <= 0) {
        httpd_resp_send_500(req);
        return ESP_FAIL;
    }
    buf[ret] = '\0';

    cJSON *json = cJSON_Parse(buf);
    if (!json) {
        httpd_resp_set_status(req, "400 Bad Request");
        httpd_resp_sendstr(req, "{\"status\":\"error\",\"message\":\"Invalid JSON\"}");
        return ESP_OK;
    }

    cJSON *j_ssid = cJSON_GetObjectItem(json, "ssid");
    cJSON *j_pass = cJSON_GetObjectItem(json, "password");

    if (!cJSON_IsString(j_ssid) || strlen(j_ssid->valuestring) == 0 || strlen(j_ssid->valuestring) > 32) {
        cJSON_Delete(json);
        httpd_resp_set_status(req, "400 Bad Request");
        httpd_resp_sendstr(req, "{\"status\":\"error\",\"message\":\"Invalid SSID length\"}");
        return ESP_OK;
    }

    nvs_handle_t nvs;
    if (nvs_open("wifi_cfg", NVS_READWRITE, &nvs) == ESP_OK) {
        nvs_set_str(nvs, "ssid", j_ssid->valuestring);
        if (cJSON_IsString(j_pass) && strlen(j_pass->valuestring) > 0) {
            nvs_set_str(nvs, "password", j_pass->valuestring);
        }
        nvs_set_u8(nvs, "configured", 1);
        nvs_commit(nvs);
        nvs_close(nvs);
    } else {
        cJSON_Delete(json);
        httpd_resp_send_500(req);
        return ESP_FAIL;
    }

    cJSON_Delete(json);

    httpd_resp_set_type(req, "application/json");
    httpd_resp_sendstr(req, "{\"status\":\"ok\",\"message\":\"Saved. Rebooting in 2s...\"}");

    if (!s_reboot_timer) {
        s_reboot_timer = xTimerCreate("reboot_tmr", pdMS_TO_TICKS(2000), pdFALSE, NULL, reboot_timer_callback);
    }
    xTimerStart(s_reboot_timer, 0);

    return ESP_OK;
}

httpd_handle_t start_webserver(void) {
    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    config.wildcard_uri = true;
    config.max_uri_handlers = 8;
    httpd_handle_t server = NULL;

    if (httpd_start(&server, &config) == ESP_OK) {
        httpd_uri_t uri_setup = { .uri = "/setup", .method = HTTP_GET, .handler = setup_page_handler };
        httpd_uri_t uri_root  = { .uri = "/",      .method = HTTP_GET, .handler = setup_page_handler };
        httpd_uri_t uri_scan  = { .uri = "/api/scan", .method = HTTP_GET, .handler = api_scan_handler };
        httpd_uri_t uri_save  = { .uri = "/api/save", .method = HTTP_POST, .handler = api_save_handler };
        httpd_uri_t uri_probe = { .uri = "/*",     .method = HTTP_GET, .handler = redirect_to_setup_handler };

        httpd_register_uri_handler(server, &uri_setup);
        httpd_register_uri_handler(server, &uri_root);
        httpd_register_uri_handler(server, &uri_scan);
        httpd_register_uri_handler(server, &uri_save);
        httpd_register_uri_handler(server, &uri_probe);
    }
    return server;
}
