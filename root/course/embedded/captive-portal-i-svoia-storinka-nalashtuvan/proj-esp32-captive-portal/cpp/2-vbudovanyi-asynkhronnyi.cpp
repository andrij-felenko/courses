#include <memory>
#include <span>
#include <string_view>
#include <vector>
#include <string>
#include "esp_http_server.h"
#include "esp_wifi.h"
#include "esp_log.h"
#include "esp_system.h"
#include "nvs_flash.h"
#include "nvs.h"
#include "cJSON.h"
#include "freertos/FreeRTOS.h"
#include "freertos/timers.h"

extern const uint8_t index_html_gz_start[] asm("_binary_index_html_gz_start");
extern const uint8_t index_html_gz_end[]   asm("_binary_index_html_gz_end");

namespace embedded::web {

class NvsStorage {
public:
    static bool saveCredentials(std::string_view ssid, std::string_view pass) noexcept {
        nvs_handle_t handle{};
        if (nvs_open("wifi_cfg", NVS_READWRITE, &handle) != ESP_OK) {
            return false;
        }

        struct NvsGuard {
            nvs_handle_t h;
            ~NvsGuard() { nvs_close(h); }
        } guard{handle};

        std::string s(ssid);
        std::string p(pass);
        nvs_set_str(handle, "ssid", s.c_str());
        nvs_set_str(handle, "password", p.c_str());
        nvs_set_u8(handle, "configured", 1);
        return nvs_commit(handle) == ESP_OK;
    }
};

class PortalHttpServer {
public:
    static esp_err_t redirectToSetup(httpd_req_t *req) noexcept {
        httpd_resp_set_status(req, "302 Found");
        httpd_resp_set_hdr(req, "Location", "http://192.168.4.1/setup");
        httpd_resp_set_hdr(req, "Cache-Control", "no-cache, no-store, must-revalidate");
        httpd_resp_send(req, nullptr, 0);
        return ESP_OK;
    }

    static esp_err_t serveGzipSpa(httpd_req_t *req) noexcept {
        const size_t len = index_html_gz_end - index_html_gz_start;
        httpd_resp_set_type(req, "text/html");
        httpd_resp_set_hdr(req, "Content-Encoding", "gzip");
        httpd_resp_set_hdr(req, "Cache-Control", "no-cache, no-store, must-revalidate");
        httpd_resp_send(req, reinterpret_cast<const char*>(index_html_gz_start), len);
        return ESP_OK;
    }

    static esp_err_t handleApiSave(httpd_req_t *req) noexcept {
        std::vector<char> buffer(256, 0);
        int bytesRead = httpd_req_recv(req, buffer.data(), buffer.size() - 1);
        if (bytesRead <= 0) {
            httpd_resp_send_500(req);
            return ESP_FAIL;
        }

        cJSON *root = cJSON_Parse(buffer.data());
        if (!root) {
            httpd_resp_set_status(req, "400 Bad Request");
            httpd_resp_sendstr(req, "{\"status\":\"error\",\"msg\":\"Bad JSON\"}");
            return ESP_OK;
        }

        struct JsonGuard {
            cJSON *obj;
            ~JsonGuard() { if (obj) cJSON_Delete(obj); }
        } guard{root};

        cJSON *jSsid = cJSON_GetObjectItem(root, "ssid");
        cJSON *jPass = cJSON_GetObjectItem(root, "password");

        if (!cJSON_IsString(jSsid) || strlen(j_ssid->valuestring) == 0 || strlen(j_ssid->valuestring) > 32) {
            httpd_resp_set_status(req, "400 Bad Request");
            httpd_resp_sendstr(req, "{\"status\":\"error\",\"msg\":\"Invalid SSID length\"}");
            return ESP_OK;
        }

        std::string_view ssidStr = jSsid->valuestring;
        std::string_view passStr = cJSON_IsString(jPass) ? jPass->valuestring : "";

        if (NvsStorage::saveCredentials(ssidStr, passStr)) {
            httpd_resp_set_type(req, "application/json");
            httpd_resp_sendstr(req, "{\"status\":\"ok\",\"msg\":\"Saved. Rebooting in 2s...\"}");

            static TimerHandle_t rebootTimer = xTimerCreate(
                "cpp_reboot", pdMS_TO_TICKS(2000), pdFALSE, nullptr,
                [](TimerHandle_t) { esp_restart(); });
            xTimerStart(rebootTimer, 0);
        } else {
            httpd_resp_send_500(req);
        }
        return ESP_OK;
    }
};

} // namespace embedded::web
