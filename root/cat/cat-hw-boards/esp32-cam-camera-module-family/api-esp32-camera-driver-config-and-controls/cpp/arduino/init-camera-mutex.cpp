#include <Arduino.h>
#include "esp_camera.h"

static SemaphoreHandle_t camera_mutex = nullptr;

void init_camera_mutex() {
    camera_mutex = xSemaphoreCreateMutex();
}

void set_camera_framesize_safe(framesize_t size) {
    if (camera_mutex != nullptr && xSemaphoreTake(camera_mutex, pdMS_TO_TICKS(1000)) == pdTRUE) {
        sensor_t *s = esp_camera_sensor_get();
        if (s != nullptr) {
            s->set_framesize(s, size);
        }
        xSemaphoreGive(camera_mutex);
    }
}
