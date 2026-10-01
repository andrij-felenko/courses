#include "esp_camera.h"
#include "WiFi.h"
#include "esp_http_server.h"

// Обробник кадрів під платформу Arduino
void send_camera_frame(httpd_req_t *req) {
    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb) {
        httpd_resp_send_500(req);
        return;
    }

    // Обов'язкове повернення буфера навіть при помилці відправки
    esp_err_t res = httpd_resp_send(req, (const char *)fb->buf, fb->len);
    esp_camera_fb_return(fb);
}
