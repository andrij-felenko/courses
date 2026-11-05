#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"
#include "esp_log.h"

static SemaphoreHandle_t xReentrantLock = NULL;
static const char *TAG = "REENTRANT_DEMO";

void internal_sensor_read(void) {
    // Повторне захоплення замка в тій самій задачі (рекурсивний вхід)
    if (xSemaphoreTakeRecursive(xReentrantLock, portMAX_DELAY) == pdTRUE) {
        ESP_LOGI(TAG, "Внутрішній шар: замок успішно захоплено повторно");
        // Читання апаратних регістрів шини
        xSemaphoreGiveRecursive(xReentrantLock);
    }
}

void external_driver_access(void) {
    if (xSemaphoreTakeRecursive(xReentrantLock, portMAX_DELAY) == pdTRUE) {
        ESP_LOGI(TAG, "Зовнішній шар: замок захоплено вперше");
        internal_sensor_read(); // Вкладений виклик
        xSemaphoreGiveRecursive(xReentrantLock);
    }
}

void app_main(void) {
    xReentrantLock = xSemaphoreCreateRecursiveMutex();
    if (xReentrantLock != NULL) {
        external_driver_access();
    }
}
