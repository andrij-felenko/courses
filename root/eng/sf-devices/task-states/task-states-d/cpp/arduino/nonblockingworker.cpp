#include <Arduino.h>
#include <FreeRTOS.h>
#include <semphr.h>
#include <queue.h>

// C++ клас неблокувального обробника подій
class NonBlockingWorker {
private:
    QueueHandle_t msgQueue;
    SemaphoreHandle_t resourceMutex;

public:
    NonBlockingWorker() {
        msgQueue = xQueueCreate(10, sizeof(uint32_t));
        // М'ютекс у FreeRTOS за замовчуванням підтримує успадкування пріоритету
        resourceMutex = xSemaphoreCreateMutex();
    }

    // Головний неблокувальний цикл задачі
    void runLoop() {
        uint32_t val;
        while (1) {
            // Очікування події з черги (стан Blocked) замість busy waiting
            if (xQueueReceive(msgQueue, &val, pdMS_TO_TICKS(500)) == pdTRUE) {
                processMessage(val);
            }
            // Звільнення кванта часу при відсутності повідомлень
            taskYIELD();
        }
    }

    void processMessage(uint32_t val) {
        if (xSemaphoreTake(resourceMutex, pdMS_TO_TICKS(50)) == pdTRUE) {
            // Обробка даних із захистом від інверсії пріоритетів
            xSemaphoreGive(resourceMutex);
        }
    }

    bool postMessage(uint32_t val) {
        return (xQueueSend(msgQueue, &val, 0) == pdTRUE);
    }
};
