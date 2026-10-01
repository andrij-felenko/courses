#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"
#include "esp_camera.h"

static SemaphoreHandle_t camera_mutex = NULL;

void init_camera_mutex(void) {
    camera_mutex = xSemaphoreCreateMutex();
}

void set_camera_framesize_safe(framesize_t size) {
    if (camera_mutex != NULL && xSemaphoreTake(camera_mutex, pdMS_TO_TICKS(1000)) == pdTRUE) {
        sensor_t *s = esp_camera_sensor_get();
        if (s != NULL) {
            s->set_framesize(s, size);
        }
        xSemaphoreGive(camera_mutex);
    }
}
