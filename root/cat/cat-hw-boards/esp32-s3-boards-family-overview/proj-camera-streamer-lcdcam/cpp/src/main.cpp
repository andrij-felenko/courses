#include <cstdio>
#include "esp_log.h"
#include "esp_system.h"
#include "esp_heap_caps.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#include "FrameBuffer.hpp"
#include "CameraDmaDriver.hpp"
#include "FrameServer.hpp"
#include "MjpegStreamer.hpp"
#include "UvcTransmitter.hpp"

static const char* TAG = "MainApp";

extern "C" void app_main(void) {
    ESP_LOGI(TAG, "--- Запуск системної прошивки кадрового сервера ESP32-S3 ---");

    // Перевірка наявності та розміру зовнішньої пам'яті PSRAM
    size_t psramSize = heap_caps_get_free_size(MALLOC_CAP_SPIRAM);
    ESP_LOGI(TAG, "Вільна пам'ять PSRAM: %zu байт (%zu КБ)", psramSize, psramSize / 1024);

    if (psramSize == 0) {
        ESP_LOGE(TAG, "УВАГА: PSRAM не виявлено або не ініціалізовано! Робота з відеокадрами обмежена.");
    }

    // 1. Налаштування конфігурації камери
    camera::CameraConfig camConfig = {};
    camConfig.width = 640;
    camConfig.height = 480;
    camConfig.format = camera::PixelFormat::JPEG;
    camConfig.dmaBufferCount = 4;
    camConfig.dmaBufferSize = 32768;
    camConfig.maxFrameSize = 128000;

    // 2. Створення екземплярів основних модулів
    auto cameraDriver = std::make_unique<camera::CameraDmaDriver>();
    auto frameServer = std::make_unique<camera::FrameServer>(8);
    auto mjpegStreamer = std::make_unique<camera::MjpegStreamer>(8080);
    auto uvcTransmitter = std::make_unique<camera::UvcTransmitter>();

    // 3. Ініціалізація та запуск драйвера DMA камери
    if (cameraDriver->init(camConfig) != ESP_OK) {
        ESP_LOGE(TAG, "Критична помилка: Не вдалося ініціалізувати CameraDmaDriver");
        return;
    }

    if (cameraDriver->startStream() != ESP_OK) {
        ESP_LOGE(TAG, "Критична помилка: Не вдалося запустити відеопотік DMA");
        return;
    }

    // 4. Запуск центрального кадрового сервера
    if (frameServer->start(*cameraDriver, 5, 4096) != ESP_OK) {
        ESP_LOGE(TAG, "Критична помилка: Не вдалося запустити FrameServer");
        return;
    }

    // 5. Запуск мережевого MJPEG передавача
    if (mjpegStreamer->start(*frameServer, 4, 8192) != ESP_OK) {
        ESP_LOGW(TAG, "Не вдалося запустити MJPEG Streamer");
    }

    // 6. Ініціалізація та запуск UVC передавача через USB OTG
    if (uvcTransmitter->init() == ESP_OK) {
        uvcTransmitter->start(*frameServer, 5, 4096);
    }

    ESP_LOGI(TAG, "Усі відеосервіси успішно ініціалізовано та запущено.");

    // Фоновий цикл моніторингу стану системи
    while (true) {
        vTaskDelay(pdMS_TO_TICKS(5000));

        size_t freeHeap = heap_caps_get_free_size(MALLOC_CAP_INTERNAL);
        size_t freePsram = heap_caps_get_free_size(MALLOC_CAP_SPIRAM);
        size_t subscribers = frameServer->subscriberCount();
        size_t httpClients = mjpegStreamer->activeClients();

        ESP_LOGI(TAG, "[Статус системи] SRAM: %zu КБ | PSRAM: %zu КБ | Підписників: %zu | HTTP клієнтів: %zu | UVC: %s",
                 freeHeap / 1024,
                 freePsram / 1024,
                 subscribers,
                 httpClients,
                 uvcTransmitter->isConnected() ? "Підключено" : "Відключено");
    }
}
