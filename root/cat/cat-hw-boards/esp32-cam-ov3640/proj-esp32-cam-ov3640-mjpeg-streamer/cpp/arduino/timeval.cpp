#include "esp_http_server.h"
#include "esp_camera.h"

#define PART_BOUNDARY "123456789000000000000987654321"
static const char* STREAM_TYPE = "multipart/x-mixed-replace; boundary=" PART_BOUNDARY;

// Метод обробки MJPEG-потоку для Arduino ESP32
esp_err_t handle_mjpeg_stream(httpd_req_t *req) {
    camera_fb_t * fb = NULL;
    esp_err_t res = ESP_OK;
    char buffer[128];

    int sock = httpd_req_to_sockfd(req);
    struct timeval to;
    to.tv_sec = 2;
    to.tv_usec = 0;
    setsockopt(sock, SOL_SOCKET, SO_SNDTIMEO, &to, sizeof(to));

    httpd_resp_set_type(req, STREAM_TYPE);
    httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");

    while(true) {
        fb = esp_camera_fb_get();
        if (!fb) {
            res = ESP_FAIL;
            break;
        }

        size_t hlen = snprintf(buffer, sizeof(buffer),
                               "\r\n--" PART_BOUNDARY "\r\n"
                               "Content-Type: image/jpeg\r\n"
                               "Content-Length: %u\r\n\r\n",
                               (unsigned int)fb->len);

        res = httpd_resp_send_chunk(req, buffer, hlen);
        if(res == ESP_OK) {
            res = httpd_resp_send_chunk(req, (const char *)fb->buf, fb->len);
        }

        esp_camera_fb_return(fb);
        fb = NULL;

        if(res != ESP_OK) {
            break;
        }
    }

    return res;
}
