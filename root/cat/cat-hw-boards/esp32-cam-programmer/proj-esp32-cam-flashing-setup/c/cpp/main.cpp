#include "camera_manager.hpp"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static const char* TAG = "main_cpp";

extern "C" void app_main() {
    ESP_LOGI(TAG, "Запуск C++-прошивки для ESP32-CAM з використанням RAII");

    esp32_cam::CameraManager camera;

    if (camera.init() != ESP_OK) {
        ESP_LOGE(TAG, "Не вдалося ініціалізувати CameraManager, зупинка виконанння");
        return;
    }

    uint32_t cycle_count = 0;

    while (true) {
        ++cycle_count;
        ESP_LOGI(TAG, "Запит кадру у C++-стилі (цикл #%lu)...", static_cast<unsigned long>(cycle_count));

        // Отримання RAII-обгортки фреймбуфера
        auto frame = camera.capture_frame();

        if (!frame) {
            ESP_LOGE(TAG, "Помилка під час захоплення кадру у циклі #%lu", static_cast<unsigned long>(cycle_count));
        } else {
            const auto bytes = frame.data();
            ESP_LOGI(TAG, "[C++ RAII] Кадр #%lu завантажено: %zu байт, %dx%d px, адреса даних: %p",
                     static_cast<unsigned long>(cycle_count),
                     bytes.size(),
                     frame.width(),
                     frame.height(),
                     static_cast<const void*>(bytes.data()));
        }

        // Автоматичне звільнення ресурсу фреймбуфера відбувається при виході об'єкта frame з області видимості циклу!

        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
