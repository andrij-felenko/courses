#ifndef MJPEG_SERVER_H
#define MJPEG_SERVER_H

#include "esp_err.h"

// Запуск HTTP-сервера потокового MJPEG-відео
esp_err_t start_mjpeg_server(void);

// Зупинка HTTP-сервера
esp_err_t stop_mjpeg_server(void);

#endif // MJPEG_SERVER_H
