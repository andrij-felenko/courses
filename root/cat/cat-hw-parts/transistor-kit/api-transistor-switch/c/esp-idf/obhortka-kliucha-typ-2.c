#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static sw_t pump = { .pin = GPIO_NUM_5, .active_low = false };  // NPN низом: «1» вмикає
static sw_t lamp = { .pin = GPIO_NUM_6, .active_low = true  };  // PNP верхом: «0» вмикає

void app_main(void) {
    ESP_ERROR_CHECK(sw_begin(&pump));
    ESP_ERROR_CHECK(sw_begin(&lamp));      // обидва стартують ВИМКНЕНИМИ

    while (1) {
        sw_on(&pump);                      // «увімкнути насос» — байдуже, що там NPN
        vTaskDelay(pdMS_TO_TICKS(3000));
        sw_off(&pump);
        sw_toggle(&lamp);                  // перемкнути лампу в протилежний стан
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
