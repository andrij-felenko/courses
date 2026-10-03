#include "esp_http_server.h"
#include "esp_camera.h"
#include "esp_log.h"
#include <stdlib.h>
#include <string.h>

// Обробник REST-ендпоінта керування сенсором OV3640
esp_err_t cmd_handler(httpd_req_t *req) {
    char param[64];
    
    // Отримання query-параметрів із URI запиту
    if (httpd_req_get_url_query_str(req, param, sizeof(param)) == ESP_OK) {
        char variable[16];
        char value[16];
        if (httpd_query_key_value(param, "var", variable, sizeof(variable)) == ESP_OK &&
            httpd_query_key_value(param, "val", value, sizeof(value)) == ESP_OK) {
            
            sensor_t *s = esp_camera_sensor_get();
            if (!s) {
                httpd_resp_send_500(req);
                return ESP_FAIL;
            }

            int val_int = atoi(value);
            int res = 0;

            if (strcmp(variable, "framesize") == 0) {
                // Зміна роздільності вимагає системного скидання DMA-каналів
                if (s->pixformat == PIXFORMAT_JPEG) {
                    res = s->set_framesize(s, (framesize_t)val_int);
                }
            } else if (strcmp(variable, "aec") == 0) {
                res = s->set_exposure_ctrl(s, val_int);
            } else if (strcmp(variable, "awb") == 0) {
                res = s->set_whitebal(s, val_int);
            } else if (strcmp(variable, "gain") == 0) {
                res = s->set_gain_ctrl(s, val_int);
            }

            if (res < 0) {
                httpd_resp_send_500(req);
                return ESP_FAIL;
            }
        }
    }

    httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");
    return httpd_resp_send(req, "{\"status\":\"ok\"}", HTTPD_RESP_USE_STRLEN);
}
