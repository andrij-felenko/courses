#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "nvs_flash.h"
#include "UsbDongle.hpp"

static const char* TAG = "MAIN";

extern "C" void app_main() {
    // Ініціалізація енергонезалежної пам'яті NVS (необхідна для роботи Wi-Fi стеку)
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);

    ESP_LOGI(TAG, "Запуск C++ об'єктно-орієнтованої прошивки для ESP32-S3-Zero");

    // Створення екземпляра головного класу-оркестратора USB-донгла
    esp32_zero::UsbDongle dongle;

    // Ініціалізація периферійних модулів та підключення до Wi-Fi мережі
    if (!dongle.begin("Dongle_WiFi_Net", "SecretPass123")) {
        ESP_LOGE(TAG, "Критична помилка ініціалізації периферії USB-донгла");
        return;
    }

    // Безкінечний неблокувальний цикл обробки асинхронних подій
    while (true) {
        dongle.update();
        vTaskDelay(pdMS_TO_TICKS(10)); // Поступаємося часом планивальнику FreeRTOS
    }
}
