#include "esp_camera.h"
#include "driver/gpio.h"

#define CAM_PIN_PWDN 32

void power_save_enter(void) {
    esp_camera_deinit();
    gpio_set_direction(CAM_PIN_PWDN, GPIO_MODE_OUTPUT);
    gpio_set_level(CAM_PIN_PWDN, 1);
}

void power_save_exit(void) {
    gpio_set_level(CAM_PIN_PWDN, 0);
    vTaskDelay(pdMS_TO_TICKS(10));
}
