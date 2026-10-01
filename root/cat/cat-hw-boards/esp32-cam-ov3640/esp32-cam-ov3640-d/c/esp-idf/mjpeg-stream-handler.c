#include "esp_camera.h"
#include "esp_log.h"
#include "esp_http_server.h"

static const char *TAG = "stream_server";

// Обробник HTTP-запиту для передачі відеопотоку MJPEG
esp_err_t mjpeg_stream_handler(httpd_req_t *req) {
    camera_fb_t *fb = NULL;
    esp_err_t res = ESP_OK;
    char part_buf[128];

    res = httpd_resp_set_type(req, "multipart/x-mixed-replace; boundary=123456789000000000000987654321");
    if (res != ESP_OK) {
        return res;
    }

    while (true) {
        // Отримання найновішого кадру з драйвера
        fb = esp_camera_fb_get();
        if (!fb) {
            ESP_LOGE(TAG, "Не вдалося отримати кадр камери");
            res = ESP_FAIL;
            break;
        }

        // Формування заголовка кадру MJPEG
        size_t hlen = snprintf(part_buf, sizeof(part_buf),
                               "\r\n--123456789000000000000987654321\r\nContent-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n",
                               fb->len);

        // Відправка заголовка та бінарного буфера в мережевий сокет
        res = httpd_resp_send_chunk(req, part_buf, hlen);
        if (res == ESP_OK) {
            res = httpd_resp_send_chunk(req, (const char *)fb->buf, fb->len);
        }

        // Критично важливе повернення буфера у драйверний пул
        esp_camera_fb_return(fb);
        fb = NULL;

        if (res != ESP_OK) {
            // При помилці сокета виходити з циклу
            break;
        }
    }

    return res;
}
