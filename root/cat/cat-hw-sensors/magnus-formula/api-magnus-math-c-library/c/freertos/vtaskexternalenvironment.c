#include "FreeRTOS.h"
#include "task.h"

// Задача 1: Моніторинг зовнішнього давача (стек задачі 1)
void vTaskExternalEnvironment(void *pvParameters) {
    float temp = 22.5f, rh = 60.0f;
    float dew_point = 0.0f;

    for (;;) {
        // Чистий повторно входжуваний виклик API — без використання м'ютексів
        if (magnus_dew_point_safe(temp, rh, &MAGNUS_PARAMS_WATER, &dew_point) == MAGNUS_OK) {
            // Обробка обчисленого значення
        }
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}

// Задача 2: Моніторинг внутрішнього відсіку (стек задачі 2)
void vTaskInternalEnclosure(void *pvParameters) {
    float temp = 45.0f, rh = 30.0f;
    float dew_point = 0.0f;

    for (;;) {
        // Паралельний виклик тієї ж функції з іншої задачі повністю безпечний
        if (magnus_dew_point_safe(temp, rh, &MAGNUS_PARAMS_WATER, &dew_point) == MAGNUS_OK) {
            // Обробка обчисленого значення
        }
        vTaskDelay(pdMS_TO_TICKS(500));
    }
}
