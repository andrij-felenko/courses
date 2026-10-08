#pragma once

#include <Arduino.h>
#include <WebServer.h>
#include "esp_camera_wrapper.hpp"

/**
 * @class MjpegStreamServer
 * @brief Мережевий контролер MJPEG-відеопотоку на базі C++ класу WebServer.
 *
 * Відповідає за обробку HTTP-запитів, реєстрацію маршруту `/stream` з передачею
 * заголовків multipart/x-mixed-replace та потокову трансляцію кадрів у реальному часі.
 */
class MjpegStreamServer {
public:
    /**
     * @brief Конструктор вебсервера трансляції.
     * @param camera Посилання на ініціалізований екземпляр EspCamera.
     * @param port Мережевий порт HTTP-сервера (типово 80).
     */
    MjpegStreamServer(EspCamera& camera, uint16_t port = 80);

    /**
     * @brief Деструктор класу MjpegStreamServer.
     */
    ~MjpegStreamServer();

    /**
     * @brief Запуск HTTP-сервера та реєстрація маршрутів.
     */
    void begin();

    /**
     * @brief Зупинка HTTP-сервера.
     */
    void stop();

    /**
     * @brief Обслуговування клієнтських запитів. Викликається у циклі loop().
     */
    void handleClient();

    /**
     * @brief Перевірка активного стану сервера.
     */
    bool isRunning() const noexcept { return is_running_; }

private:
    EspCamera& camera_;
    WebServer server_;
    bool is_running_ = false;
    String boundary_ = "123456789000000000000987654321";

    /**
     * @brief Обробник головної сторінки `/` із вбудованим HTML-плеєром.
     */
    void handleRoot();

    /**
     * @brief HTTP-ендпоінт `/stream` для покадрової потокової трансляції MJPEG.
     */
    void handleStream();

    /**
     * @brief Обробник неіснуючих сторінок (404 Not Found).
     */
    void handleNotFound();
};
