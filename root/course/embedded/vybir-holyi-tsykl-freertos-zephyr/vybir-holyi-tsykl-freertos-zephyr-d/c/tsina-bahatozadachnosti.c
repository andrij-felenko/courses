#include "FreeRTOS.h"
#include "task.h"
#include "queue.h"
#include <stdint.h>

typedef struct {
    uint32_t timestamp;
    float temperature;
} sensor_msg_t;

static QueueHandle_t s_sensor_queue = NULL;

void vTaskSensor(void *pvParameters) {
    (void)pvParameters;
    sensor_msg_t msg = {0};

    for (;;) {
        // Імітація зчитування сенсора
        msg.timestamp = xTaskGetTickCount();
        msg.temperature = 24.5f;

        // Відправка в чергу з блокуванням до 10 мс
        if (s_sensor_queue != NULL) {
            xQueueSend(s_sensor_queue, &msg, pdMS_TO_TICKS(10));
        }

        // Періодичний сон на 100 мс (процесор віддається іншим задачам)
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

void vTaskDisplay(void *pvParameters) {
    (void)pvParameters;
    sensor_msg_t received_msg;

    for (;;) {
        // Очікування повідомлення з черги (блокування без споживання CPU)
        if (xQueueReceive(s_sensor_queue, &received_msg, portMAX_DELAY) == pdTRUE) {
            // Оновлення дисплея отриманими даними
            (void)received_msg;
        }
    }
}

void freertos_app_start(void) {
    s_sensor_queue = xQueueCreate(8, sizeof(sensor_msg_t));

    // Створення задач із виділенням індивідуальних стеків
    xTaskCreate(vTaskSensor,  "Sensor",  256, NULL, tskIDLE_PRIORITY + 2, NULL); // 256 слів = 1024 Б
    xTaskCreate(vTaskDisplay, "Display", 512, NULL, tskIDLE_PRIORITY + 1, NULL); // 512 слів = 2048 Б

    vTaskStartScheduler();
}
