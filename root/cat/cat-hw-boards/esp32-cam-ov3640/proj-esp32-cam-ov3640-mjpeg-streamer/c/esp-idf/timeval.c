#include "esp_http_server.h"
#include "esp_camera.h"
#include "esp_log.h"
#include <sys/socket.h>

#define STREAM_BOUNDARY "123456789000000000000987654321"
static const char* STREAM_CONTENT_TYPE = "multipart/x-mixed-replace; boundary=" STREAM_BOUNDARY;

// Обробник HTTP-запиту для відправки потоку MJPEG
esp_err_t mjpeg_stream_handler(httpd_req_t *req) {
    camera_fb_t *fb = NULL;
    esp_err_t res = ESP_OK;
    char part_buf[128];

    // Налаштування тайм-ауту сокета для запобігання блокуванню
    int sockfd = httpd_req_to_sockfd(req);
    struct timeval timeout = { .tv_sec = 2, .tv_usec = 0 };
    setsockopt(sockfd, SOL_SOCKET, SO_SNDTIMEO, &timeout, sizeof(timeout));

    res = httpd_resp_set_type(req, STREAM_CONTENT_TYPE);
    if (res != ESP_OK) {
        return res;
    }

    httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");

    while (true) {
        // Отримання кадрового буфера із зовнішньої пам'яті PSRAM
        fb = esp_camera_fb_get();
        if (!fb) {
            ESP_LOGE("MJPEG", "Помилка захоплення кадру з сенсора");
            res = ESP_FAIL;
            break;
        }

        // Формування MIME-заголовка кадру з межовим розділювачем boundary
        size_t hlen = snprintf(part_buf, sizeof(part_buf),
                               "\r\n--" STREAM_BOUNDARY "\r\n"
                               "Content-Type: image/jpeg\r\n"
                               "Content-Length: %u\r\n\r\n",
                               (unsigned int)fb->len);

        // Відправка заголовка клієнту через TCP-сокет
        res = httpd_resp_send_chunk(req, part_buf, hlen);
        if (res == ESP_OK) {
            // Відправка бінарних даних JPEG з буфера PSRAM
            res = httpd_resp_send_chunk(req, (const char *)fb->buf, fb->len);
        }

        // Повернення кадрового буфера в драйвер камери
        esp_camera_fb_return(fb);
        fb = NULL;

        if (res != ESP_OK) {
            // При розриві зв'язку або тайм-ауті виходимо з циклу
            ESP_LOGW("MJPEG", "Розрив TCP-з'єднання або переповнення вікна");
            break;
        }
    }

    return res;
}
