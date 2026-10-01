#ifndef HTTP_STREAM_SERVER_HPP
#define HTTP_STREAM_SERVER_HPP

#include <esp_log.h>
#include <esp_http_server.h>
#include "camera_driver.hpp"

namespace esp32s3 {

class HttpStreamServer {
public:
    explicit HttpStreamServer(CameraDriver& camera) : camera_(camera) {}

    ~HttpStreamServer() {
        stop();
    }

    bool start(uint16_t port = 80) {
        if (server_handle_) {
            return true;
        }

        httpd_config_t config = HTTPD_DEFAULT_CONFIG();
        config.server_port = port;
        config.ctrl_port = port + 1;
        config.max_open_sockets = 4;
        config.stack_size = 8192;

        esp_err_t err = httpd_start(&server_handle_, &config);
        if (err != ESP_OK) {
            ESP_LOGE(TAG, "Не вдалося запустити HTTP-сервер: 0x%x", err);
            return false;
        }

        httpd_uri_t stream_uri = {
            .uri = "/stream",
            .method = HTTP_GET,
            .handler = stream_handler,
            .user_ctx = this
        };

        httpd_register_uri_handler(server_handle_, &stream_uri);
        ESP_LOGI(TAG, "MJPEG HTTP-відеосервер запущено на порту %d (URI: /stream)", port);
        return true;
    }

    void stop() {
        if (server_handle_) {
            httpd_stop(server_handle_);
            server_handle_ = nullptr;
            ESP_LOGI(TAG, "HTTP-відеосервер зупинено");
        }
    }

private:
    static constexpr const char* TAG = "HttpStreamServer";
    static constexpr const char* STREAM_CONTENT_TYPE = "multipart/x-mixed-replace; boundary=frame_boundary";
    static constexpr const char* STREAM_BOUNDARY = "\r\n--frame_boundary\r\n";
    static constexpr const char* STREAM_PART = "Content-Type: image/jpeg\r\nContent-Length: %u\r\n\r\n";

    static esp_err_t stream_handler(httpd_req_t* req) {
        auto* self = static_cast<HttpStreamServer*>(req->user_ctx);
        if (!self) {
            return ESP_FAIL;
        }

        esp_err_t res = httpd_resp_set_type(req, STREAM_CONTENT_TYPE);
        if (res != ESP_OK) {
            return res;
        }

        httpd_resp_set_hdr(req, "Access-Control-Allow-Origin", "*");

        char part_buf[128];
        while (true) {
            auto frame = self->camera_.capture();
            if (!frame || !frame->data()) {
                vTaskDelay(pdMS_TO_TICKS(10));
                continue;
            }

            res = httpd_resp_send_chunk(req, STREAM_BOUNDARY, strlen(STREAM_BOUNDARY));
            if (res != ESP_OK) {
                break;
            }

            size_t hlen = snprintf(part_buf, sizeof(part_buf), STREAM_PART, frame->size());
            res = httpd_resp_send_chunk(req, part_buf, hlen);
            if (res != ESP_OK) {
                break;
            }

            res = httpd_resp_send_chunk(req, reinterpret_cast<const char*>(frame->data()), frame->size());
            if (res != ESP_OK) {
                break;
            }

            vTaskDelay(pdMS_TO_TICKS(30)); // Близько 30 FPS
        }

        return res;
    }

    CameraDriver& camera_;
    httpd_handle_t server_handle_{nullptr};
};

} // namespace esp32s3

#endif // HTTP_STREAM_SERVER_HPP
