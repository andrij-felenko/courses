#include <stdio.h>
#include <stdbool.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"

// Спільний ресурс (буфер даних) для витісняльної моделі
static float g_sensor_data = 0.0f;
static SemaphoreHandle_t g_data_mutex = NULL;

// Кооперативна задача: добровільно передає управління через taskYIELD()
void vCooperativeTask(void *pvParameters) {
    while (1) {
        // Крок 1: виконання частини роботи
        printf("Cooperative task step 1\n");

        // Добровільна віддача процесорного ресурсу (Yield)
        taskYIELD();

        // Крок 2: виконання другої частини роботи
        printf("Cooperative task step 2\n");
        taskYIELD();
    }
}

// Витісняльна високопріоритетна задача: захищає спільний ресурс м'ютексом
void vPreemptiveHighPriorityTask(void *pvParameters) {
    while (1) {
        // Витісняє низькопріоритетні задачі при появі події або розблокуванні
        if (xSemaphoreTake(g_data_mutex, portMAX_DELAY) == pdTRUE) {
            // Критична секція доступу до даних
            g_sensor_data += 1.5f;
            xSemaphoreGive(g_data_mutex);
        }
        vTaskDelay(pdMS_TO_TICKS(10)); // Входить у стан очікування таймера
    }
}

void app_main(void) {
    g_data_mutex = xSemaphoreCreateMutex();

    // Створення задач із різними пріоритетами для витісняльного планувальника
    xTaskCreate(vCooperativeTask, "CoopTask", 2048, NULL, 1, NULL);
    xTaskCreate(vPreemptiveHighPriorityTask, "PreemptTask", 2048, NULL, 2, NULL);
}
