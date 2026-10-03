#include "esp_http_server.h"
#include "esp_camera.h"

// Обробник контрольних AJAX-запитів для модуля камери
esp_err_t handle_control(httpd_req_t *req) {
    char query[64];
    if (httpd_req_get_url_query_str(req, query, sizeof(query)) == ESP_OK) {
        char var[16], val[16];
        if (httpd_query_key_value(query, "var", var, sizeof(var)) == ESP_OK &&
            httpd_query_key_value(query, "val", val, sizeof(val)) == ESP_OK) {
            
            sensor_t *s = esp_camera_sensor_get();
            int value = atoi(val);

            if (strcmp(var, "framesize") == 0) {
                s->set_framesize(s, (framesize_t)value);
            } else if (strcmp(var, "aec") == 0) {
                s->set_exposure_ctrl(s, value);
            } else if (strcmp(var, "awb") == 0) {
                s->set_whitebal(s, value);
            }
        }
    }
    httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
    return httpd_resp_send(req, "{\"status\":\"ok\"}", HTTPD_RESP_USE_STRLEN);
}
