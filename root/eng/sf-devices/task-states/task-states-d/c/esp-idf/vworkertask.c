#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"

static TaskHandle_t xWorkerHandle = NULL;

// Задача обробки, яку можна призупиняти та відновлювати
void vWorkerTask(void *pvParameters) {
    while (1) {
        // Виконання частки обчислень
        vDoHeavyComputationStep();

        // Добровільне віддання залишку кванта часу задачам такого ж пріоритету
        taskYIELD();
    }
}

// Управляюча задача: контролює життєвий цикл фонового воркера
void vControlTask(void *pvParameters) {
    while (1) {
        // Призупинення задачі воркера (перехід у Suspended)
        ESP_LOGI("CTRL", "Призупинення фонової задачи...");
        vTaskSuspend(xWorkerHandle);

        // Перебування у стані Blocked на 2 секунди
        vTaskDelay(pdMS_TO_TICKS(2000));

        // Явне відновлення призупиненої задачі (перехід у Ready)
        ESP_LOGI("CTRL", "Відновлення фонової задачи...");
        vTaskResume(xWorkerHandle);

        vTaskDelay(pdMS_TO_TICKS(2000));
    }
}
