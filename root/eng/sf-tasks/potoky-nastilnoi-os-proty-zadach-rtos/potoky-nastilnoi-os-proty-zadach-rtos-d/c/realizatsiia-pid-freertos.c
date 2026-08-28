#include "FreeRTOS.h"
#include "task.h"
#include "semphr.h"

// Статичні змінні для гарантованого виділення пам'яті без купи
#define TASK_STACK_SIZE 256
static StackType_t xTaskStack[TASK_STACK_SIZE];
static StaticTask_t xTaskBuffer;
static SemaphoreHandle_t xSpiMutex;
static StaticSemaphore_t xMutexBuffer;

void vControlLoopTask(void *pvParameters) {
    TickType_t xLastWakeTime;
    const TickType_t xFrequency = pdMS_TO_TICKS(1); // Період 1 мс

    // Ініціалізація точки відліку часу
    xLastWakeTime = xTaskGetTickCount();

    for (;;) {
        // Очікування настання наступного абсолютного моменту часу
        vTaskDelayUntil(&xLastWakeTime, xFrequency);

        // Захоплення м'ютекса з підтримкою Priority Inheritance
        if (xSemaphoreTake(xSpiMutex, pdMS_TO_TICKS(0)) == pdTRUE) {
            // Читання датчика та генерація сигналу керування
            // Час виконання: строго детермінований (наприклад, 45 мкс)
            xSemaphoreGive(xSpiMutex);
        }
    }
}

void app_main(void) {
    // Створення м'ютекса з підтримкою успадкування пріоритетів
    xSpiMutex = xSemaphoreCreateMutexStatic(&xMutexBuffer);

    // Створення задачі з максимальним пріоритетом
    xTaskCreateStatic(
        vControlLoopTask,
        "ControlTask",
        TASK_STACK_SIZE,
        NULL,
        configMAX_PRIORITIES - 1, // Найвищий пріоритет
        xTaskStack,
        &xTaskBuffer
    );
}
