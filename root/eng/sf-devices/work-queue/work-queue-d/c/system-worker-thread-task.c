#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"

// Головна функція системного робочого потоку (Worker Thread)
void system_worker_thread_task(void *pvParameters) {
    QueueHandle_t work_queue = (QueueHandle_t)pvParameters;
    work_item_t current_item;

    for (;;) {
        // Очікування появи елемента у черзі (потік блокується, 0% CPU)
        if (xQueueReceive(work_queue, &current_item, portMAX_DELAY) == pdTRUE) {
            // Перевірка та виклик функції зворотного виклику
            if (current_item.func != NULL) {
                current_item.func(current_item.arg);
            }
        }
    }
}
