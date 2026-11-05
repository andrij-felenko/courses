#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

TaskHandle_t xTask2Handle = NULL;

void vTask1(void *pvParameters) {
    while (1) {
        // Перехід у стан Blocked на 100 мс
        // Задача не споживає процесорний час під час очікування
        vTaskDelay(pdMS_TO_TICKS(100));

        // Призупинення другої задачі (перехід у Suspended)
        if (xTask2Handle != NULL) {
            vTaskSuspend(xTask2Handle);
        }
    }
}

void vTask2(void *pvParameters) {
    while (1) {
        // Виконання корисних обчислень
        vDoWork();
        vTaskDelay(pdMS_TO_TICKS(50));
    }
}
