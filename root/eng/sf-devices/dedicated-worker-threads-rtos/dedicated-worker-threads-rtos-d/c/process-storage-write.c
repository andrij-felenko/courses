#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include "freertos/semphr.h"

// Перелік команд потоку-виконавця
typedef enum {
    WORKER_CMD_STORAGE_WRITE,
    WORKER_CMD_SENSOR_READ,
    WORKER_CMD_TERMINATE
} worker_cmd_type_t;

// Структура повідомлення черги
typedef struct {
    worker_cmd_type_t command;
    uint32_t target_address;
    uint8_t *data_buffer;
    size_t length;
    SemaphoreHandle_t completion_sem;
} worker_msg_t;

// Контекст окремого потоку-виконавця
typedef struct {
    QueueHandle_t queue_handle;
    TaskHandle_t task_handle;
} dedicated_worker_t;

// Внутрішня функція обробки запису в накопичувач
static void process_storage_write(uint32_t addr, const uint8_t *data, size_t len) {
    // Симуляція тривалого запису у фізичний накопичувач
    vTaskDelay(pdMS_TO_TICKS(20));
}

// Головний цикл подій потоку-виконавця
static void worker_thread_entry(void *pvParameters) {
    dedicated_worker_t *worker = (dedicated_worker_t *)pvParameters;
    worker_msg_t msg;

    for (;;) {
        // Потік блокується в очікуванні повідомлення з черги (0% CPU)
        if (xQueueReceive(worker->queue_handle, &msg, portMAX_DELAY) == pdTRUE) {
            switch (msg.command) {
                case WORKER_CMD_STORAGE_WRITE:
                    process_storage_write(msg.target_address, msg.data_buffer, msg.length);
                    break;

                case WORKER_CMD_SENSOR_READ:
                    // Обробка даних давача
                    break;

                case WORKER_CMD_TERMINATE:
                    if (msg.completion_sem != NULL) {
                        xSemaphoreGive(msg.completion_sem);
                    }
                    vTaskDelete(NULL);
                    return;

                default:
                    break;
            }

            // Якщо виклик синхронний — сигналізуємо клієнту про завершення
            if (msg.completion_sem != NULL) {
                xSemaphoreGive(msg.completion_sem);
            }
        }
    }
}

// Ініціалізація та запуск потоку-виконавця
bool dedicated_worker_init(dedicated_worker_t *worker, UBaseType_t priority, uint32_t stack_depth) {
    worker->queue_handle = xQueueCreate(10, sizeof(worker_msg_t));
    if (worker->queue_handle == NULL) {
        return false;
    }

    BaseType_t status = xTaskCreate(
        worker_thread_entry,
        "DedicatedWorker",
        stack_depth,
        worker,
        priority,
        &worker->task_handle
    );

    return (status == pdPASS);
}

// Асинхронна відправка команди у потік
bool dedicated_worker_post_async(dedicated_worker_t *worker, worker_cmd_type_t cmd, uint32_t addr, uint8_t *buf, size_t len) {
    worker_msg_t msg = {
        .command = cmd,
        .target_address = addr,
        .data_buffer = buf,
        .length = len,
        .completion_sem = NULL
    };

    return (xQueueSend(worker->queue_handle, &msg, 0) == pdTRUE);
}

// Синхронна відправка команди з чеканням відповіді
bool dedicated_worker_post_sync(dedicated_worker_t *worker, worker_cmd_type_t cmd, uint32_t addr, uint8_t *buf, size_t len, TickType_t timeout) {
    SemaphoreHandle_t sync_sem = xSemaphoreCreateBinary();
    if (sync_sem == NULL) {
        return false;
    }

    worker_msg_t msg = {
        .command = cmd,
        .target_address = addr,
        .data_buffer = buf,
        .length = len,
        .completion_sem = sync_sem
    };

    if (xQueueSend(worker->queue_handle, &msg, timeout) != pdTRUE) {
        vSemaphoreDelete(sync_sem);
        return false;
    }

    bool success = (xSemaphoreTake(sync_sem, timeout) == pdTRUE);
    vSemaphoreDelete(sync_sem);
    return success;
}
