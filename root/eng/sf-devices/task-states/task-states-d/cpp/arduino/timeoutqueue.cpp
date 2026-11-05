#include <Arduino.h>
#include <FreeRTOS.h>
#include <queue.h>

// C++ обгортка для безпечної роботи з чергою та таймаутами
template <typename T>
class TimeoutQueue {
private:
    QueueHandle_t handle;

public:
    TimeoutQueue(UBaseType_t length) {
        handle = xQueueCreate(length, sizeof(T));
    }

    // Метод очікування елемента з черги з поверненням успішності
    bool pop(T &item, uint32_t timeoutMs) {
        TickType_t ticks = pdMS_TO_TICKS(timeoutMs);
        // Звернення до ядра RTOS: перехід у Blocked при відсутності даних
        return (xQueueReceive(handle, &item, ticks) == pdTRUE);
    }

    bool pushFromISR(const T &item) {
        BaseType_t xHigherPriorityTaskWoken = pdFALSE;
        BaseType_t res = xQueueSendFromISR(handle, &item, &xHigherPriorityTaskWoken);
        if (xHigherPriorityTaskWoken) {
            portYIELD_FROM_ISR();
        }
        return (res == pdTRUE);
    }
};
