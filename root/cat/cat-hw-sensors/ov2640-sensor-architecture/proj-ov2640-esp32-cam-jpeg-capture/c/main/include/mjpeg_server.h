#ifndef MJPEG_SERVER_H
#define MJPEG_SERVER_H

#include <stdint.h>
#include <stdbool.h>
#include "esp_err.h"
#include "esp_http_server.h"

#ifdef __cplusplus
extern "C" {
#endif

#define MJPEG_SERVER_PORT   80
#define MJPEG_URI_STREAM    "/stream"
#define MJPEG_STREAM_BOUNDARY "123456789000000000000987654321"

/**
 * @brief Запуск HTTP-сервера для трансляції відеопотоку у форматі MJPEG.
 *
 * Створює екземпляр esp_http_server на порту 80 та реєструє URI-обробник /stream.
 *
 * @return Дескриптор запущенного сервера (httpd_handle_t) або NULL у разі помилки.
 */
httpd_handle_t mjpeg_server_start(void);

/**
 * @brief Зупинка HTTP-сервера потокового відео.
 *
 * @param server Дескриптор запущенного сервера.
 * @return ESP_OK у разі успішної зупинки.
 */
esp_err_t mjpeg_server_stop(httpd_handle_t server);

#ifdef __cplusplus
}
#endif

#endif /* MJPEG_SERVER_H */
