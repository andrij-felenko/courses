#include <Arduino.h>
#include <FreeRTOS.h>
#include <queue.h>

void workerThreadTask(void* parameter) {
    QueueHandle_t queue = static_cast<QueueHandle_t>(parameter);
    DeferredWorkItem item;

    while (true) {
        // Перехід у блокований стан до надходження нового елемента
        if (xQueueReceive(queue, &item, portMAX_DELAY) == pdTRUE) {
            item.execute();
        }
    }
}
