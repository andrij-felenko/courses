#ifndef MJPEG_STREAM_SERVER_H
#define MJPEG_STREAM_SERVER_H

#include "esp_err.h"
#include "esp_http_server.h"

#ifdef __cplusplus
extern "C" {
#endif

#define HTTP_STREAM_PORT      80
#define STREAM_BOUNDARY       "123456789000000000000987654321"
#define STREAM_CONTENT_TYPE   "multipart/x-mixed-replace;boundary=" STREAM_BOUNDARY

/**
 * @brief Запуск HTTP-вебсервера потокового мовлення MJPEG.
 *
 * @param server_handle Указник для збереження дескриптора створеного сервера
 * @return esp_err_t ESP_OK у разі успішного запуску
 */
esp_err_t mjpeg_stream_server_start(httpd_handle_t *server_handle);

/**
 * @brief Зупинка HTTP-вебсервера та звільнення мережевих сокетів.
 *
 * @param server_handle Дескриптор діючого HTTP-сервера
 * @return esp_err_t ESP_OK у разі успішної зупинки
 */
esp_err_t mjpeg_stream_server_stop(httpd_handle_t server_handle);

#ifdef __cplusplus
}
#endif

#endif /* MJPEG_STREAM_SERVER_H */
