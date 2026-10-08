#ifndef HTTP_STREAM_SERVER_H
#define HTTP_STREAM_SERVER_H

#include "esp_err.h"
#include "esp_http_server.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @file http_stream_server.h
 * @brief Оголошення C-інтерфейсу асинхронного HTTP-сервера ESP-IDF для MJPEG-трансляції.
 */

#define STREAM_SERVER_PORT      80
#define STREAM_PART_BOUNDARY    "123456789000000000000987654321"
#define STREAM_CONTENT_TYPE     "multipart/x-mixed-replace; boundary=" STREAM_PART_BOUNDARY

/**
 * @brief Запуск асинхронного HTTP-сервера та реєстрація обробника потокового відео /stream.
 *
 * @return esp_err_t ESP_OK при успішному запуску, або відповідний код помилки.
 */
esp_err_t http_stream_server_start(void);

/**
 * @brief Зупинка HTTP-сервера та вивільнення сокетних ресурсів.
 *
 * @return esp_err_t ESP_OK при успішній зупинці.
 */
esp_err_t http_stream_server_stop(void);

/**
 * @brief Отримання дескриптора запущеного HTTP-сервера.
 *
 * @return httpd_handle_t Дескриптор сервера або NULL, якщо сервер не запущено.
 */
httpd_handle_t http_stream_server_get_handle(void);

#ifdef __cplusplus
}
#endif

#endif /* HTTP_STREAM_SERVER_H */
