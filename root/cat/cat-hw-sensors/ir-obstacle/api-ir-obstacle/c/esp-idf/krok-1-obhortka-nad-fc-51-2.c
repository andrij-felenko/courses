#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"

static const char   *TAG = "ir";
static ir_obstacle_t front;   // OUT давача на GPIO4, дебаунс 8 мс

static void ir_task(void *arg) {
    for (;;) {
        ir_obstacle_update(&front);              // опитати давач (неблокуюче)
        ESP_LOGI(TAG, "%s", ir_obstacle(&front) ? "ПЕРЕШКОДА" : "вільно");
        vTaskDelay(pdMS_TO_TICKS(2));            // крок опитування
    }
}

void app_main(void) {
    ESP_ERROR_CHECK(ir_obstacle_begin(&front, GPIO_NUM_4, 8, true));
    xTaskCreate(ir_task, "ir", 2048, NULL, 5, NULL);
    // інші задачі живуть паралельно — опитування їх не блокує
}
